from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse 
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User,Post,Follow,Like
import json

def remove_like(request, post_id):  
    if request.method == "POST":  # Ensure this is a POST request  
        post = get_object_or_404(Post, pk=post_id)  
        user = request.user  # Use the request.user directly  
        
        try:  
            like = Like.objects.get(user=user, post=post)  
            like.delete()  
            return JsonResponse({"message": "unliked"})  
        except Like.DoesNotExist:  
            return JsonResponse({"error": "Like not found"}, status=404)  
    return JsonResponse({"error": "Invalid request method"}, status=405) # Handle GET requests  

def add_like(request, post_id):  
    if request.method == "POST":  # Ensure this is a POST request  
        post = get_object_or_404(Post, pk=post_id)  
        user = request.user  # Use the request.user directly  

        already_liked = Like.objects.filter(user=user, post=post).exists()  
        if not already_liked:  
            Like.objects.create(user=user, post=post)  
            return JsonResponse({"message": "liked"})  
        else:  
            return JsonResponse({"message": "Already liked"}, status=400)  
    return JsonResponse({"error": "Invalid request method"}, status=405)  # Handle GET requests  

def edit(request, post_id):  
     if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})

def index(request):  
    all_posts = Post.objects.all().order_by("-id")  
    paginator = Paginator(all_posts, 10)  
    page_num = request.GET.get('page', 1)  
    page_post = paginator.get_page(page_num)  

    liked_post_ids = []  
    # Check if the user is authenticated before querying likes  
    if request.user.is_authenticated:  
        liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)  

    return render(request, "network/index.html", {  
        "all_posts": all_posts,  
        "page_post": page_post,  
        "liked_post": list(liked_post_ids)  # Convert to list for template  
    })  

 
def new_post(request):  
    if request.method == "POST":  # Corrected to "POST"  
        content = request.POST.get('content')  # Correct way to access POST data  
        user = request.user  # Directly use the logged-in user  
        post = Post(content=content, user=user)  
        post.save()  
        return HttpResponseRedirect(reverse("index"))  # Redirect to index after saving  

    # Handle GET request: render the new post form or redirect  
    return render(request, "network/new_post.html")  # Optional: Render a form for GET requests  

def profile(request, user_id):  
    user = get_object_or_404(User, pk=user_id)  
    # Retrieve posts only if they exist  
    all_posts = Post.objects.filter(user=user).order_by("-id")  
    
    # Debug: Log the number of posts retrieved  
    print(f"Profile View - User: {user.username}, Posts Count: {all_posts.count()}")  
    
    following = Follow.objects.filter(user=user)  
    followers = Follow.objects.filter(followeruser=user)  
    
    followers_count = followers.count()  
    following_count = following.count()  
    
     
    if request.user.is_authenticated:
       isfollowing = Follow.objects.filter(user=user, followeruser=request.user).exists()
        
    else:
       isfollowing =False
    
    # Paginate posts  
    paginator = Paginator(all_posts, 10)  
    page_num = request.GET.get('page', 1)  
    page_post = paginator.get_page(page_num)  
    
    return render(request, "network/profile.html", {  
        "allposts": all_posts,  
        "page_post": page_post,  
        "username": user.username,  
        "following": following_count,  
        "followers": followers_count,  
        "isfollowing": isfollowing,  
        "user_owner": user
    }) 
def following(request):
    currentuser = User.objects.get(pk=request.user.id) 
    following_people=Follow.objects.filter(user=currentuser)
    allposts=Post.objects.all().order_by("-id")
    following_posts=[]
    for post in allposts:
        for person in following_people:
            if person.followeruser==post.user:
                following_posts.append(post)
    
    
    paginator = Paginator(following_posts,10)
    page_num=request.GET.get('page',1)
    page_post = paginator.get_page(page_num)
    liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)  
 
    return render(request, "network/following.html",{
        "page_post":page_post,
        "liked_post": list(liked_post_ids)
    })
              


def follow(request):
    if request.method == "POST":  
        user_follow = request.POST.get("userfollow") 
    
    try:  
            # Ensure user_follow_id is a valid integer  
            user_follow = int(user_follow)  # Convert to integer  
    except (ValueError, TypeError):  
            # Handle cases where the conversion fails (invalid ID)  
            # You could log an error message or redirect back with a warning  
            return redirect('profile', user_id=request.user.id)  # or wherever you want to redirect  

        # Use get_object_or_404 to fetch user by ID  
    user_follow_data = get_object_or_404(User, pk=user_follow)  

        # Optionally, check if the user is trying to follow themselves  
    if request.user == user_follow_data:  
            # Handle the case (e.g., return an error, log, or redirect)  
            return redirect('profile', user_id=user_follow_data.id)  

        # Create a new Follow object  
    Follow.objects.create(user=user_follow_data, followeruser=request.user)  
        
        # Redirect where appropriate, perhaps back to the profile  
    return redirect('profile', user_id=user_follow_data.id) 
def unfollow(request):  
    if request.method == "POST":  
        user_follow = request.POST.get("userfollow")  

        # Debugging: Log the user_follow_id value  
        print(f"user_follow_id (unfollow): {user_follow}")  

        try:  
            user_follow = int(user_follow)  # Convert to integer  
        except (ValueError, TypeError):  
            # Handle invalid ID case  
            return redirect('profile', user_id=request.user.id)  

        # Fetch the user to unfollow  
        user_follow_data = get_object_or_404(User, pk=user_follow)  

        # Get the current user  
        current_user = request.user  

        # Attempt to get the Follow object  
        try:  
            follow_instance = Follow.objects.get(user=user_follow_data, followeruser=current_user)  
            follow_instance.delete()  # Delete the follow relationship  
        except Follow.DoesNotExist:  
            # Optionally handle the case where the follow relationship does not exist  
            print(f"No follow relationship found for {current_user} following {user_follow_data}")  # Debugging output  

        # Redirect back to the profile of the user being unfollowed  
        return redirect('profile', user_id=user_follow_data.id)  

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
