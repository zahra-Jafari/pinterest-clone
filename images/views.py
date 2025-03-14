from django.shortcuts import render, redirect, get_object_or_404
from .models import Image, Like, Comment, Category, UserProfile
from .forms import ImageForm, CommentForm, CategoryForm, SignUpForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import logout, authenticate, login
from .forms import CustomLoginForm
from django.contrib import messages
from .models import Profile
import os


# def profile_view(request):
#     if request.method == "POST":
#         form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
#         if form.is_valid():
#             form.save()
#             return redirect('profile')  # یا مسیر دلخواه شما
#     else:
#         form = UserProfileForm(instance=request.user.profile)
#
#     return render(request, 'profile.html', {'form': form})


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        # اگر دکمه "حذف عکس" کلیک شده باشد
        if "delete_picture" in request.POST:
            if profile.profile_picture:
                # حذف فایل عکس از سرور
                if os.path.exists(profile.profile_picture.path):
                    os.remove(profile.profile_picture.path)
                # حذف عکس از دیتابیس (برمی‌گردد به عکس دیفالت)
                profile.profile_picture = None
                profile.save()
            return redirect('profile')

        # اگر عکس جدید آپلود شده باشد
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form, 'profile': profile})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('image_list')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def image_list(request):
    category_id = request.GET.get('category')
    if category_id:
        try:
            images = Image.objects.filter(categories__id=category_id)
        except Category.DoesNotExist:
            images = Image.objects.none()
    else:
        images = Image.objects.all().order_by('-created_at')

    return render(request, 'image_list.html', {'images': images})


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required
def image_upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()

            new_category_name = form.cleaned_data.get('new_category')
            if new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
                if created:
                    print(f'New category created: {category.name}')
                image.categories.add(category)

            form.save_m2m()

            return redirect('success')

    else:
        form = ImageForm()

    return render(request, 'upload.html', {'form': form})


def success_view(request):
    return render(request, 'success.html')


def image_detail(request, id):
    image = get_object_or_404(Image, id=id)

    if request.method == 'POST' and 'like' in request.POST:
        Like.objects.get_or_create(image=image, user=request.user)
        return redirect('image_detail', id=image.id)

    if request.method == 'POST' and 'comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.image = image
            comment.user = request.user
            comment.save()
            return redirect('image_detail', id=image.id)
    else:
        comment_form = CommentForm()

    return render(request, 'images/image_detail.html', {'image': image, 'comment_form': comment_form})


def image_like(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    Like.objects.get_or_create(image=image, user=request.user)
    return redirect('image_detail', image_id=image.id)


def custom_logout_view(request):
    logout(request)
    return redirect('image_list')


# @login_required
# def profile_view(request):
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
#         if form.is_valid():
#             form.save()
#             return redirect('profile')
#     else:
#         form = UserProfileForm(instance=user_profile)
#
#     context = {
#         'user': request.user,
#         'user_profile': user_profile,
#         'form': form,
#     }
#     return render(request, 'profile.html')


# def profile_view(request):
#     profile, created = Profile.objects.get_or_create(user=request.user)  # اگر پروفایل وجود ندارد، ایجاد کن
#
#     if request.method == "POST":
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('profile')  # بعد از تغییر عکس، صفحه را رفرش کن
#     else:
#         form = UserProfileForm(instance=profile)
#
#     return render(request, 'profile.html', {'form': form, 'profile': profile})
