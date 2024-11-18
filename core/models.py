from django.db import models

# Create your models here.
   export async function getServerSideProps({ params }) {
       const res = await fetch(`https://api.example.com/products/${params.id}`);
       const product = await res.json();
       return { props: { product } };
   }
   
   
   
   
