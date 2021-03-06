from rest_framework import generics
from django.views.generic import DetailView
from . import models
from rest_framework.permissions import IsAuthenticated, AllowAny
from . import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError, PermissionDenied, ParseError
from customer.models import User
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import requests
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .youtube import upload_video
import os
from django.conf import settings


class ListCategories(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Categories.objects.all()
    serializer_class = serializers.CategoriesSerializer


# Create product


class CreateProduct(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_serializer_context(self):
        return {'is_created': True, 'request': self.request.user}

    def perform_create(self, serializer):
        user = self.request.user
        if (user.is_seller):
            if serializer.is_valid():
                if 'image' in self.request.data:
                    product_data = serializer.save()
                    imageSerializer = serializers.ImageSerializer(
                        data={'product_id': product_data.id, 'photo_url': self.request.data['image']})
                    if imageSerializer.is_valid():
                        img = imageSerializer.save()
                    else:
                        product_data.delete()
                        raise ValidationError(
                            {'Detail': imageSerializer.errors})

                else:
                    raise ParseError({'Detail': 'image field is required'})

                if 'image2' in self.request.data:
                    imageSerializer2 = serializers.ImageSerializer(
                        data={'product_id': product_data.id, 'photo_url': self.request.data['image2']})
                    if imageSerializer2.is_valid():
                        img2 = imageSerializer2.save()
                    else:
                        product_data.delete()
                        img.delete()
                        raise ValidationError(
                            {'Detail': imageSerializer2.errors})

                if 'image3' in self.request.data:
                    imageSerializer3 = serializers.ImageSerializer(
                        data={'product_id': product_data.id, 'photo_url': self.request.data['image3']})
                    if imageSerializer3.is_valid():
                        imageSerializer3.save()
                    else:
                        product_data.delete()
                        img.delete()
                        img2.delete()
                        raise ValidationError(
                            {'Detail': imageSerializer3.errors})

        else:
            raise PermissionDenied(
                {'Detail': 'User cannot upload the product'})

# Update products


class ProductUpdate(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def perform_update(self, serializer):
        current_user = self.request.user
        current_object = models.Product.objects.get(id=self.kwargs['pk'])
        if(current_user.id != current_object.user_id_id):
            raise PermissionDenied(
                {'Detail': 'User cannot update the product'})

        return super().perform_update(serializer)

# List all products


class ListAllProduct(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        # obj = models.Categories.objects.extra(
        #     select={'lower_name': 'lower(cat_name)'}).order_by('lower_name')
        user = self.request.user
        if user.id == None:
            return models.Product.objects.all().order_by('-created_at')
        return models.Product.objects.filter(user_id_id=user.id).order_by('-created_at')

    def get_serializer_context(self):
        return {'is_list': True}


# List single product details

class ProductDetail(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


# Delete Products

class ProductDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def perform_destroy(self, instance):
        current_user = self.request.user
        current_object = models.Product.objects.get(id=self.kwargs['pk'])
        if(current_user.id != current_object.user_id_id):
            raise PermissionDenied(
                {'Detail': 'User cannot delete the product'})
        return super().perform_destroy(instance)


# List products by categories

class ListProductsByCategories(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        try:
            category_id = models.Categories.objects.get(
                cat_name__iexact=self.kwargs['category']).id
        except models.Categories.DoesNotExist:
            raise Http404({'details': 'Category Not Found'})
        query = models.Product.objects.filter(categories=category_id)
        return query

# Search Products by keywords


class SearchProduct(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        query = models.Product.objects.filter(
            product_name__icontains=self.kwargs['keyword'])
        return query

# Search Image


class SearchImage(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}

# Create Image


class CreateImage(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer


# Create Products reviews

class CreateProductReview(generics.ListCreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.ProductReview.objects.all()
    serializer_class = serializers.ProductReviewSerializer

# Create Products rating


class CreateProductRating(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.ProductRating.objects.all()
    serializer_class = serializers.ProductRatingSerializer

    def perform_create(self, serializer):
        userId = self.request.data['user_id']
        productId = self.request.data['product_id']
        try:
            obj = models.ProductRating.objects.get(
                user_id_id=userId, product_id_id=productId)
        except models.ProductRating.DoesNotExist:
            obj = None

        if(obj == None):
            temp = super().perform_create(serializer)
            return temp
        else:
            obj.rating = int(self.request.data['rating'])
            obj.save()


# Add to Cart


class CreateCart(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer


class UpdateCart(generics.UpdateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer


class RemoveCart(generics.DestroyAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer


class RemoveAllFromCart(generics.DestroyAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer

    def delete(self, request, *args, **kwargs):
        object = models.Cart.objects.filter(user_id_id=self.kwargs['pk'])
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCartItem(generics.ListAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer

    def get_queryset(self):
        query = models.Cart.objects.filter(user_id_id=self.kwargs['pk'])
        return query

# Manage Sales


class CreateSales(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Sales.objects.all()
    serializer_class = serializers.SaleSerializer

# Payment Section


def performKhaltiPayment(token, amount):
    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {'token': token, 'amount': amount}
    headers = {
        'Authorization': 'Key test_secret_key_005817a9e285430d84c855be761eb8c4'}
    response = requests.post(url, payload, headers=headers)
    return response


class CreatePayment(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer

    def create(self, serializer):
        serializer = self.get_serializer(data=self.request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def perform_create(self, serializer):
        db_state = transaction.savepoint()
        amount = 0
        for item in serializer.data:
            product = models.Product.objects.get(id=item['product_id'])
            if(product.product_quantity > item['quantity']):
                with transaction.atomic():
                    product.product_quantity -= item['quantity']
                    product.save()
                    amount += int(item['price'])
            else:
                transaction.savepoint_rollback(db_state)
                raise ValidationError(
                    {'detail': 'Ordered Item {} is higher than the stock'.format(product.product_name)})
        khalti_token = self.request.data[0]['token']
        khalti_response = performKhaltiPayment(khalti_token, amount)
        if(khalti_response.status_code >= 200 and khalti_response.status_code < 400):
            pment = serializer.save()
            for i in pment:
                sale = serializers.SaleSerializer(
                    data={'user_id': self.request.user.id, 'payment_id': i.id})
                if sale.is_valid():
                    sale.save()
                else:
                    raise ValidationError({'detail': sale.errors})
            transaction.savepoint_commit(db_state)
        else:
            transaction.savepoint_rollback(db_state)
            raise ValidationError(khalti_response.content)


class ListPayment(generics.ListAPIView):
    permission_class = (IsAuthenticated)
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer

    def get_queryset(self):
        obj = models.Payment.objects.filter(user_id_id=self.request.user.id)
        return obj

# Course Parts

# Create Tests


class CreateTest(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Test
    serializer_class = serializers.TestSerializer


class RetrieveTest(generics.ListAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Test
    serializer_class = serializers.TestSerializer

    def get_queryset(self):
        test = models.Test.objects.filter(course_id_id=self.kwargs['pk'])
        print(test)
        return test

# Create Questions


class CreateQuestions(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Questions
    serializer_class = serializers.QuestionsSerializer

class CreateReport(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Report
    serializer_class = serializers.ReportSerializer

    def perform_create(self, serializer):
        serializer.save()
        totalQuestion = self.request.data['total_question']
        score = self.request.data['score']
        progressTest = (int(score)/(int)(totalQuestion)) * 20
        progress_obj = models.Progress.objects.get(
            user_id_id=self.request.data['user_id'], course_id_id=self.request.data['course_id'])
        progress_obj.progress_percentage += progressTest
        progress_obj.save()



# Create course

class CreateCourse(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    def perform_create(self, serializer):
        temp = super().perform_create(serializer)
        return temp

# Video Upload


class CreateVideo(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.Video.objects.all()
    serializer_class = serializers.VideoSerializer

    def create(self, request, *args, **kwargs):
        videoFile = request.data['file']
        path = default_storage.save(
            videoFile.name, ContentFile(videoFile.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        videoDetail = {
            'title': request.data['title'],
            'file': tmp_file
        }
        res = upload_video.uploadVid(videoDetail)
        if 'id' in res:
            print('success with id: %s' % res['id'])
            print(type(id))
            request.data['video_url'] = str(res['id'])
        return super().create(request, *args, **kwargs)


class CreateWatchList(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.WatchList.objects.all()
    serializer_class = serializers.WatchListSerializer

    def perform_create(self, serializer):
        serializer.save()
        watch_obj = models.WatchList.objects.filter(
            user_id_id=self.request.data['user_id'],course_id_id = self.request.data['course_id'])
        watch_video = watch_obj.count()
        total_video = models.Video.objects.filter(
            course_id_id=self.request.data['course_id']).count()
        progress_per_video = (1/total_video) * 80
        print(watch_obj)
        progress_obj = models.Progress.objects.get(
            user_id_id=self.request.data['user_id'], course_id_id=self.request.data['course_id'])
        progress_obj.progress_percentage += progress_per_video
        progress_obj.save()


# List Videos

class ListCourse(generics.ListAPIView):
    permission_class = (AllowAny,)
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.id == None:
            return models.Course.objects.all().order_by('-created_at')
        return models.Course.objects.filter(user_id_id=user.id).order_by('-created_at')

    def get_serializer_context(self):
        try:
            temp = models.Enrolled.objects.get(user_id_id=self.request.user.id)
        except ObjectDoesNotExist:
            print(self.request.data)
        return {'is_list': True}


class CourseDetail(generics.RetrieveAPIView):
    permission_class = (AllowAny,)
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    def get_serializer_context(self):
        print('-----------------------------------')
        course = models.Enrolled.objects.filter(course_id_id=self.kwargs['pk'])
        print(course)
        if course.count() == 0:
            return {'is_list': False, 'is_enrolled': False , 'current_user':self.request.user}
        print(self.request.user.id)
        for item in course:
            print(item.user_id_id)
            if item.user_id_id == self.request.user.id:
                return {'is_list': False, 'is_enrolled': True , 'current_user':self.request.user}
        return {'is_list': False, 'is_enrolled': False , 'current_user':self.request.user}


# Course Update

class CourseUpdate(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    def perform_update(self, serializer):
        current_user = self.request.user
        current_object = models.Course.objects.get(id=self.kwargs['pk'])
        if(current_user.id != current_object.user_id_id):
            raise PermissionDenied(
                {'Detail': 'User cannot update the Course'})

        return super().perform_update(serializer)


class CourseDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    def perform_destroy(self, instance):
        current_user = self.request.user
        current_object = models.Course.objects.get(id=self.kwargs['pk'])
        if(current_user.id != current_object.user_id_id):
            raise PermissionDenied(
                {'Detail': 'User cannot delete the course'})
        return super().perform_destroy(instance)


class Enrolled(generics.CreateAPIView):
    permission_class = (AllowAny)
    queryset = models.Enrolled.objects.all()
    serializer_class = serializers.EnrolledSerializer


class CreateCoursePayment(generics.CreateAPIView):
    permission_class = (IsAuthenticated)
    queryset = models.CoursePayment.objects.all()
    serializer_class = serializers.CoursePaymentSerializer

    def perform_create(self, serializer):
        khalti_token = self.request.data['token']
        price = self.request.data['price']

        khalti_response = performKhaltiPayment(khalti_token, price)
        if (khalti_response.status_code >= 200 and khalti_response.status_code < 400):
            pment = serializer.save()
            enroll = serializers.EnrolledSerializer(
                data={'user_id': self.request.user.id, 'course_id': self.request.data['course_id'], 'payment_id': pment.id})
            if enroll.is_valid():
                enroll.save()
                models.Progress.objects.create(
                    user_id_id=self.request.user.id, course_id_id=self.request.data['course_id'], progress_percentage=0.0)
            else:
                raise ValidationError({'detail': enroll.errors})

# Create Products reviews

class CreateCourseReview(generics.ListCreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.CourseReview.objects.all()
    serializer_class = serializers.CourseReviewSerializer

# Create Products rating


class CreateCourseRating(generics.CreateAPIView):
    permission_class = (IsAuthenticated,)
    queryset = models.CourseRating.objects.all()
    serializer_class = serializers.CourseRatingSerializer

    def perform_create(self, serializer):
        userId = self.request.data['user_id']
        courseId = self.request.data['course_id']
        try:
            obj = models.CourseRating.objects.get(
                user_id_id=userId, course_id_id=courseId)
        except models.CourseRating.DoesNotExist:
            obj = None

        if(obj == None):
            temp = super().perform_create(serializer)
            return temp
        else:
            obj.rating = int(self.request.data['rating'])
            obj.save()