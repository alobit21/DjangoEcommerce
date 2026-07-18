import requests
import hashlib
import hmac
import json
from decimal import Decimal
from django.conf import settings
from .models import Payment
from .models import Payment as PaymentModel


class ClickPesaService:
    """
    ClickPesa API integration service for mobile money payments.

    Authentication flow (per ClickPesa docs):
      1. POST /generate-token  →  receive JWT (already prefixed with "Bearer ")
      2. Use that JWT in Authorization header for all subsequent calls

    Payment flow:
      1. POST /payments/preview-ussd-push-request  →  validate details & check active channels
      2. POST /payments/initiate-ussd-push-request →  send USSD push to customer's phone

    Payout flow:
      1. POST /payouts/preview-mobile-money-payout →  validate & check fee/balance
      2. POST /payouts/initiate-mobile-money-payout (if you add it later)
    """

    BASE_URL = "https://api.clickpesa.com/third-parties"


    def __init__(self):
        self.client_id = settings.CLICKPESA_CLIENT_ID
        self.api_key = settings.CLICKPESA_API_KEY
        self.secret_key = getattr(settings, 'CLICKPESA_SECRET_KEY', '')

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def generate_token(self):
        """
        Generate a JWT authorization token from ClickPesa.

        ClickPesa docs:
          POST /generate-token
          Headers: client-id, api-key
          Response: { success: bool, token: "Bearer eyJ..." }

        The returned token string already contains the "Bearer " prefix.
        Token is valid for 1 hour.
        """
        url = f"{self.BASE_URL}/generate-token"
        headers = {
            'client-id': self.client_id,
            'api-key': self.api_key,
            'Content-Type': 'application/json',
        }

        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if not data.get('success'):
            raise ValueError(f"ClickPesa token generation failed: {data}")

        # 'token' already includes the "Bearer " prefix per the docs
        return data['token']

    def _get_auth_headers(self, token):
        """
        Build request headers using the provided JWT token.
        Token already contains the 'Bearer ' prefix as returned by generate_token().
        """
        return {
            'Authorization': token,
            'Content-Type': 'application/json',
        }

    # ------------------------------------------------------------------
    # Checksum (optional security layer)
    # ------------------------------------------------------------------

    def _generate_checksum(self, payload: dict) -> str | None:
        """
        Generate HMAC-SHA256 checksum for request payload validation.
        Only generated when CLICKPESA_SECRET_KEY is configured in settings.

        The payload is serialised to JSON with sorted keys before hashing
        so that the signature is deterministic.
        """
        if not self.secret_key:
            return None

        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

        checksum = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return checksum

    # ------------------------------------------------------------------
    # Payment: Step 1 – Preview USSD push
    # ------------------------------------------------------------------

    def preview_ussd_push(self, token: str, amount: str, phone_number: str,
                          order_reference: str, fetch_sender_details: bool = False) -> dict:
        """
        Validate push details and verify payment channel availability.

        ClickPesa docs:
          POST /payments/preview-ussd-push-request
          Body fields (camelCase):
            amount          string   required
            currency        string   required  ("TZS")
            orderReference  string   required
            phoneNumber     string   optional
            fetchSenderDetails bool  default false
            checksum        string   optional

        Response includes:
          activeMethods: list of available channels for the phone number
          sender:        sender details (if fetchSenderDetails=true)
        """
        url = f"{self.BASE_URL}/payments/preview-ussd-push-request"

        payload = {
            'amount': amount,
            'currency': 'TZS',
            'orderReference': order_reference,
            'phoneNumber': phone_number,
            'fetchSenderDetails': fetch_sender_details,
        }

        checksum = self._generate_checksum(payload)
        if checksum:
            payload['checksum'] = checksum

        response = requests.post(
            url,
            headers=self._get_auth_headers(token),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Payment: Step 2 – Initiate USSD push
    # ------------------------------------------------------------------

    def initiate_ussd_push(self, token: str, amount: str, phone_number: str,
                           order_reference: str) -> dict:
        """
        Send the USSD push request to the customer's mobile device.

        ClickPesa docs:
          POST /payments/initiate-ussd-push-request
          Body fields (camelCase):
            amount          string   required
            currency        string   required  ("TZS")
            orderReference  string   required
            phoneNumber     string   required
            checksum        string   optional

        Response:
          id                string   – unique transaction identifier
          status            string   – PROCESSING | SUCCESS | FAILED | SETTLED
          channel           string   – e.g. TIGO-PESA, M-PESA, AIRTEL-MONEY
          orderReference    string
          collectedAmount   string
          collectedCurrency string
          createdAt         datetime
          clientId          string
        """
        url = f"{self.BASE_URL}/payments/initiate-ussd-push-request"

        payload = {
            'amount': amount,
            'currency': 'TZS',
            'orderReference': order_reference,
            'phoneNumber': phone_number,
        }

        checksum = self._generate_checksum(payload)
        if checksum:
            payload['checksum'] = checksum

        response = requests.post(
            url,
            headers=self._get_auth_headers(token),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # High-level: initiate mobile money payment
    # ------------------------------------------------------------------

    def initiate_mobile_money_payment(self, payment, phone_number: str, payment_method: str) -> dict:
        """
        Full payment initiation flow:
          1. Generate JWT token
          2. Preview USSD push (validate + check active channels)
          3. Initiate USSD push (send prompt to customer's phone)
          4. Update Payment model with response data

        Args:
            payment:        Payment model instance
            phone_number:   Customer phone number (with country code, no +)
                            e.g. "255712345678"
            payment_method: Payment method string (MPESA, TIGOPESA, etc.)
                            Used for logging/record keeping; ClickPesa detects
                            the channel automatically from the phone number.

        Returns:
            dict: { success: bool, data?: dict, error?: str, payment_id: uuid }
        """
        try:
            # Step 1: Authenticate
            token = self.generate_token()

            amount = str(payment.amount)
            # Create order reference max 20 chars: ORDER + last 15 chars of ID
            order_id_str = str(payment.order.id).replace('-', '')
            order_reference = f"ORDER{order_id_str[-15:]}"

            # Step 2: Preview – validate details & confirm channel availability
            preview_data = self.preview_ussd_push(
                token=token,
                amount=amount,
                phone_number=phone_number,
                order_reference=order_reference,
            )

            active_methods = preview_data.get('activeMethods', [])
            if not active_methods:
                payment.status = PaymentModel.Status.FAILED
                payment.failure_reason = 'No active payment channels available for this phone number'
                payment.save()
                return {
                    'success': False,
                    'error': 'No active payment channels available for this phone number',
                    'payment_id': payment.id,
                }

            # Step 3: Initiate – send USSD push to customer
            result = self.initiate_ussd_push(
                token=token,
                amount=amount,
                phone_number=phone_number,
                order_reference=order_reference,
            )

            # Step 4: Persist ClickPesa response to our Payment record
            payment.clickpesa_payment_id = result.get('id')
            payment.reference_number = result.get('orderReference')
            payment.phone_number = phone_number
            payment.status = PaymentModel.Status.PROCESSING
            payment.save()

            # Reflect pending payment on the order
            payment.order.payment_status = payment.order.PaymentStatus.PENDING_PAYMENT
            payment.order.save()

            return {
                'success': True,
                'data': result,
                'payment_id': payment.id,
            }

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', error_msg)
                except Exception:
                    pass

            payment.status = PaymentModel.Status.FAILED
            payment.failure_reason = error_msg
            payment.save()

            return {
                'success': False,
                'error': error_msg,
                'payment_id': payment.id,
            }

    # ------------------------------------------------------------------
    # Check payment status
    # ------------------------------------------------------------------

    def check_payment_status(self, payment) -> dict:
        """
        Query ClickPesa for the latest status of a transaction.

        Args:
            payment: Payment model instance (must have clickpesa_payment_id set)

        Returns:
            dict: { success: bool, data?: dict, error?: str }
        """
        if not payment.clickpesa_payment_id:
            return {'success': False, 'error': 'No ClickPesa payment ID on this record'}

        try:
            token = self.generate_token()

            response = requests.get(
                f"{self.BASE_URL}/payments/{payment.clickpesa_payment_id}",
                headers=self._get_auth_headers(token),
                timeout=30,
            )
            response.raise_for_status()

            response_data = response.json()
            self._update_payment_status(payment, response_data)

            return {'success': True, 'data': response_data}

        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    # ------------------------------------------------------------------
    # Update payment status from ClickPesa response
    # ------------------------------------------------------------------

    def _update_payment_status(self, payment, clickpesa_data: dict):
        """
        Map ClickPesa transaction status to our internal Payment status and
        persist the changes, updating the related Order as well.

        ClickPesa statuses (from docs):
          PROCESSING  – push sent, awaiting customer approval
          SUCCESS     – customer approved, payment collected
          SETTLED     – funds settled to merchant account
          FAILED      – payment failed or rejected
        """
        clickpesa_status = clickpesa_data.get('status', '').upper()

        # Map only the statuses defined in the ClickPesa docs
        status_mapping = {
            'PROCESSING': PaymentModel.Status.PROCESSING,
            'SUCCESS': PaymentModel.Status.COMPLETED,
            'SETTLED': PaymentModel.Status.COMPLETED,
            'FAILED': PaymentModel.Status.FAILED,
            'CANCELLED': PaymentModel.Status.FAILED,
            'CANCELED': PaymentModel.Status.FAILED,
        }

        if clickpesa_status not in status_mapping:
            # Unknown status – log but don't crash
            return

        payment.status = status_mapping[clickpesa_status]

        # Sync orderReference if returned
        if clickpesa_data.get('orderReference'):
            payment.reference_number = clickpesa_data['orderReference']

        # Sync channel (e.g. TIGO-PESA, M-PESA, AIRTEL-MONEY)
        if clickpesa_data.get('channel'):
            payment.channel = clickpesa_data['channel']

        # Record failure reason
        if clickpesa_status == 'FAILED':
            payment.failure_reason = clickpesa_data.get('failure_reason', 'Payment failed')

        payment.save()

        # Mirror status on the Order
        if payment.status == PaymentModel.Status.COMPLETED:
            payment.order.payment_status = payment.order.PaymentStatus.PAID
        elif payment.status == PaymentModel.Status.FAILED:
            payment.order.payment_status = payment.order.PaymentStatus.PAYMENT_FAILED

        payment.order.save()

    # ------------------------------------------------------------------
    # Webhook handler
    # ------------------------------------------------------------------

    def process_webhook(self, webhook_data: dict) -> dict:
        """
        Process a webhook notification pushed by ClickPesa after a transaction
        status change.

        ClickPesa sends the same fields as the initiate response:
          id, status, orderReference, collectedAmount, collectedCurrency,
          channel, createdAt, clientId

        Args:
            webhook_data: Parsed JSON payload from the webhook POST body

        Returns:
            dict: { success: bool, payment_id?: uuid, status?: str, error?: str }
        """
        try:
            # ClickPesa uses 'id' for the transaction identifier in webhook payloads
            clickpesa_id = webhook_data.get('id')
            if not clickpesa_id:
                return {'success': False, 'error': 'No transaction id in webhook payload'}

            payment = Payment.objects.filter(clickpesa_payment_id=clickpesa_id).first()
            if not payment:
                return {
                    'success': False,
                    'error': f'No payment found for ClickPesa transaction id: {clickpesa_id}',
                }

            self._update_payment_status(payment, webhook_data)

            return {
                'success': True,
                'payment_id': payment.id,
                'status': payment.status,
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ------------------------------------------------------------------
    # Payout: Preview mobile money payout
    # ------------------------------------------------------------------

    def preview_mobile_money_payout(self, token: str, amount: float, phone_number: str,
                                    order_reference: str, currency: str = 'TZS') -> dict:
        """
        Validate payout details and retrieve fee/balance information before
        initiating an actual payout.

        ClickPesa docs:
          POST /payouts/preview-mobile-money-payout
          Body fields (camelCase):
            amount          number   required
            phoneNumber     string   required  (with country code, no +)
            currency        string   required  ("TZS" or "USD")
            orderReference  string   required
            checksum        string   optional

        Response:
          amount          – total to be deducted (includes fee)
          balance         – current account balance
          channelProvider – e.g. "TIGO PESA"
          fee             – transaction fee
          exchanged       – bool, true if currency conversion applied
          exchange        – exchange rate details (when exchanged=true)
          order           – order details
          payoutFeeBearer – "merchant" | "both" | "customer"
          receiver        – receiver details
        """
        url = f"{self.BASE_URL}/payouts/preview-mobile-money-payout"

        payload = {
            'amount': amount,
            'phoneNumber': phone_number,
            'currency': currency,
            'orderReference': order_reference,
        }

        checksum = self._generate_checksum(payload)
        if checksum:
            payload['checksum'] = checksum

        response = requests.post(
            url,
            headers=self._get_auth_headers(token),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()