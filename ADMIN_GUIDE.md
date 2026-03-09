# Ecommerce Admin Management Panel Guide

## Overview
This guide covers the comprehensive admin management panel built for your Django ecommerce application. The panel provides full CRUD functionality for products, orders, users, and stock management.

## Features Implemented

### 1. User Management
- **Extended User Profiles**: Each user now has an extended profile with phone, address, city, country, and postal code
- **Admin User**: Created admin user (username: admin, password: admin123)
- **User Search & Filter**: Search by username, email, filter by staff status, activity

### 2. Product Management
- **Full CRUD**: Create, Read, Update, Delete products
- **Category Management**: Organize products by categories
- **Image Upload**: Product images with automatic thumbnail generation
- **Stock Status**: Real-time stock level display (In Stock, Low Stock, Out of Stock)
- **Price Display**: Shows both USD and Tanzanian Shillings (TSH)

### 3. Order Management
- **Order Status Tracking**: Pending → Processing → Shipped → Delivered → Cancelled
- **Order Details**: Complete order information with items, quantities, and prices
- **Bulk Actions**: Mark multiple orders as processing, shipped, delivered, or cancelled
- **Stock Integration**: Cancelled orders automatically return items to stock

### 4. Stock Management
- **Real-time Stock Levels**: Track inventory for each product
- **Low Stock Alerts**: Visual indicators when stock falls below reorder level
- **Stock Transactions**: Complete audit trail of all stock movements
- **Bulk Stock Operations**: Add/remove stock for multiple products at once

### 5. Admin Dashboard
- **Statistics Overview**: Total orders, pending orders, products, low stock items, users
- **Recent Orders**: Quick view of latest orders
- **Top Categories**: Most popular product categories
- **Responsive Design**: Works on desktop and mobile devices

## Accessing the Admin Panel

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: `http://127.0.0.1:8000/admin/`

3. Login with:
   - Username: `admin`
   - Password: `admin123`

## Admin Sections

### Users & Groups
- **Users**: Manage all user accounts with extended profiles
- **Groups**: Create user groups for different permissions

### Products
- **Categories**: Create and manage product categories
- **Products**: Full product management with images, pricing, and stock status

### Core Management
- **Orders**: Complete order management with status tracking
- **Stock**: Inventory management with low stock alerts
- **Stock Transactions**: Audit trail of all stock movements
- **User Profiles**: Extended user information management

## Admin Actions

### Order Management
- **Mark as Processing**: Move orders to processing status
- **Mark as Shipped**: Update order status to shipped
- **Mark as Delivered**: Complete the order process
- **Cancel Orders**: Cancel orders and return items to stock

### Stock Management
- **Add Stock**: Increase inventory levels
- **Remove Stock**: Decrease inventory levels
- **Stock Adjustments**: Manual stock corrections with reason tracking

## Key Features

### Automatic Stock Creation
When a new product is created, an associated stock record is automatically created with 0 quantity.

### Stock-Order Integration
- When orders are cancelled, items are automatically returned to stock
- Stock transactions are created for all stock movements
- Low stock alerts appear in the product list

### Enhanced Search & Filtering
- Search products by name, description, category
- Filter orders by status, date, user
- Filter stock by low stock levels

### Visual Indicators
- Color-coded order status badges
- Stock level indicators (green/orange/red)
- Product thumbnails in admin lists

## Database Schema

### Core Models
- **UserProfile**: Extended user information
- **Order**: Order management with status tracking
- **OrderItem**: Individual items within orders
- **Stock**: Inventory management
- **StockTransaction**: Audit trail for stock movements

### Product Models
- **Category**: Product categorization
- **Product**: Product information with images

## Customization

### Adding New Admin Actions
Create new actions in `core/admin_actions.py` and register them in the admin classes.

### Custom Dashboard
The dashboard template is located at `templates/admin/dashboard.html` and can be customized for your needs.

### Stock Management
Modify reorder levels and add custom stock alerts through the Stock model.

## Security Considerations

1. **Admin Access**: Only staff users can access the admin panel
2. **Stock Transactions**: All stock changes are tracked with user attribution
3. **Order Management**: Order status changes are logged and auditable

## Next Steps

1. **Custom Permissions**: Set up specific permissions for different admin roles
2. **Email Notifications**: Add email alerts for low stock and new orders
3. **Reporting**: Add detailed sales and inventory reports
4. **API Integration**: Connect with external inventory systems

## Support

For issues or questions about the admin panel, check the Django admin documentation or review the code in:
- `core/admin.py` - Main admin configurations
- `products/admin.py` - Product-specific admin setup
- `core/admin_actions.py` - Custom admin actions
- `templates/admin/dashboard.html` - Dashboard template
