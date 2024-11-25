from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User


def signin(request):
    # Check if the user is already authenticated; redirect them to the dashboard if true.
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    else:
        if request.method == 'POST':
            # Retrieve email and password from the POST request.
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Authenticate user based on provided email and password.
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # Log the user in and redirect to the dashboard if authentication succeeds.
                login(request, user)
                return redirect('dashboard')
            else:
                # Display an error message for incorrect credentials.
                messages.error(request, "Account not found! Incorrect e-mail or password")
                return redirect('signin')

    # Render the sign-in page if the request method is GET or no valid login attempt.
    return render(request, 'accounts/signin.html')


@login_required
def signout(request):
    # Log the user out and redirect them to the sign-in page.
    logout(request)
    return redirect('signin')


def custom_404_view(request, exception):
    # Render a custom 404 error page.
    return render(request, '404.html', status=404)


@login_required
def profile_view(request):
    # Fetch the authenticated user's details to display in their profile.
    user = request.user
    context = {
        'user': user,
        'title' : 'Profile'
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def update_profile(request):
    # Allow the authenticated user to update their profile details.
    user = request.user
    if request.method == 'POST':
        # Update the user's profile fields based on form input.
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.gender = request.POST.get('gender')
        user.phone_number = request.POST.get('phone_number')
        user.save()  # Save changes to the database.
        return redirect('profile')  # Redirect to the profile page after updating.
    
    # Render the update profile page with the user's current details pre-filled.
    return render(request, 'accounts/update_profile.html', {'user': user})


@login_required
def change_pass(request):
    # Allow the authenticated user to change their password.
    user = request.user
    if request.method == 'POST':
        # Retrieve password inputs from the form.
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if user.check_password(old_password):  # Verify the old password is correct.
            if new_password == confirm_password:
                # Update the user's password if new and confirm passwords match.
                user.set_password(new_password)
                user.save()  # Save the new password.
                messages.success(request, "Password changed successfully")
                return redirect('profile')  # Redirect to the profile page after success.
            else:
                # Show an error if new password and confirmation do not match.
                messages.error(request, "New password and confirm password do not match")
                return redirect('change_pass')
        else:
            # Show an error if the old password is incorrect.
            messages.error(request, "Old password is incorrect")
            return redirect('change_pass')
    
    # Render the change password page if the request method is GET.
    return render(request, 'accounts/change_pass.html', {'user': user})
