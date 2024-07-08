from django.shortcuts import render
import pandas as pd
from .models import Product
from .serializers import UserSerializer, LoginSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
import csv
import numpy as np
# Create your views here.


def home(request):
    df = pd.read_csv('static/data.csv')
    Product.objects.all().delete()
    handle_missing_values(df)
    # Save the cleaned data back to the database
    for index, row in df.iterrows():
        Product.objects.get_or_create(
            product_id=row['product_id'],
            product_name = row['product_name'],
            category = row['category'],
            price = row['price'],
            quantity_sold = row['quantity_sold'],
            rating = row['rating'],
            review_Count = row['review_count']
        )
    return HttpResponse('Csv created successfully!!')
    
@api_view(['POST'])       
def signup(request):
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status = status.HTTP_201_CREATED)
    return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data = request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request,username = username,password = password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'},status = status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            


def generate_summary_report():
    df = pd.DataFrame(list(Product.objects.all().values()))
    print(df['price'])
    df['total_revenue'] = df['price']*df['quantity_sold']
    category_revenue = df.groupby('category')['total_revenue'].sum().reset_index()
    top_product = df.loc[df.groupby('category')['quantity_sold'].idxmax()]
    top_product = top_product[['category','product_name','quantity_sold']].rename(
        columns={
            'product_name': 'top_product',
            'quantity_sold': 'top_product_quantity_sold'
        }
    )
    summary_report = pd.merge(category_revenue,top_product,on='category')
    return summary_report

def download_summary_report(request):
    summary_report = generate_summary_report()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="summary_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['category', 'total_revenue', 'top_product', 'top_product_quantity_sold'])

    # Write data to CSV
    for index, row in summary_report.iterrows():
        writer.writerow(row)

    #return HttpResponse("Summary Report downloaded successfully")    
    return response

def display_summary_report(request):

    summary_report = generate_summary_report()
    report_data = summary_report.to_dict(orient='records')
    return render(request, 'product/index.html', {'report_data': report_data})

def handle_missing_values(df):
    # Ensure numeric fields are numeric
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Replace missing values with the median for price and quantity_sold
    median_price = df['price'].median()
    median_quantity_sold = df['quantity_sold'].median()

    # Handle cases where the median could be NaN
    if pd.isna(median_price):
        median_price = 0
    if pd.isna(median_quantity_sold):
        median_quantity_sold = 0

    df['price'].fillna(median_price, inplace=True)
    df['quantity_sold'].fillna(median_quantity_sold, inplace=True)

    # Calculate average rating per category
    df['rating'] = df.groupby('category')['rating'].transform(lambda x: x.fillna(x.mean()))

    # Replace remaining NaN values in 'rating' with 0
    df['rating'].fillna(0, inplace=True)

    # Ensure no NaN values remain
    df['price'].fillna(0, inplace=True)
    df['quantity_sold'].fillna(0, inplace=True)
    df['rating'].fillna(0, inplace=True)
    print(df)