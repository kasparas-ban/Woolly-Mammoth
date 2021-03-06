from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from mammoth.models import Comment, Pattern
from mammoth.forms import UserForm, UserProfileForm, PatternForm, UserProfile
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.views.generic import View
from django.http import HttpResponse
from .forms import ContactForm
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone

# Add Avg pack
from django.db.models import Avg, Max, Min

def index(request):
    visitor_cookie_handler(request)
    # This will give top 5 pattern
    comments = Comment.objects.values('pattern').order_by('pattern').annotate(Avg('rating')).order_by('-rating__avg')[0:5]
    # patterns = Pattern.objects.filter(pk__in = [comments[0]['pattern'],comments[1]['pattern'],comments[2]['pattern'],comments[3]['pattern'],comments[4]['pattern']])
    pattern1 = Pattern.objects.get(pk = comments[0]['pattern'])
    pattern2 = Pattern.objects.get(pk = comments[1]['pattern'])
    pattern3 = Pattern.objects.get(pk = comments[2]['pattern'])
    pattern4 = Pattern.objects.get(pk = comments[3]['pattern'])
    pattern5 = Pattern.objects.get(pk = comments[4]['pattern'])
    # put them in the order we want
    patterns = [pattern1,pattern2,pattern3,pattern4,pattern5]
    # get online user count

    online_users = get_current_users()
    context={"patterns":patterns,
             "online_user":online_users,                
            }
    response = render(request, 'mammoth/index.html',context)
    return response

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'mammoth/register.html', context={'user_form':user_form, 'profile_form':profile_form, 'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                # Here: we can redirect the user to the page where they used to login
                # and if it cannot get previous page, it will redirect to mammoth:index
                refer = request.META.get("HTTP_REFERER","mammoth:index") 
                # return redirect(reverse('mammoth:index'))
                return redirect(refer)  
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'mammoth/login.html')

@login_required
def restricted(request):
    return render(request, 'mammoth/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('mammoth:index'))

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits
	
	
# -------------------------------------------------------
# --- Mammoth -------------------------------------------
# -------------------------------------------------------

def pattern(request, pattern_title_slug):
    context_dict = {}
    try:
        opened_pattern = Pattern.objects.get(slug=pattern_title_slug)
        comments = Comment.objects.filter(pattern = opened_pattern.pk)
        avg_rating = comments.aggregate(Avg('rating'))

        context_dict['pattern'] = opened_pattern
        context_dict['comments'] = comments
        context_dict['AvgRating'] = avg_rating['rating__avg']
        context_dict['author'] = opened_pattern.author
        context_dict['description'] = opened_pattern.description
    except Pattern.DoesNotExist:
        context_dict['pattern'] = None
        
    return render(request, 'mammoth/pattern.html', context_dict)

def forum(request):
	return render(request, 'mammoth/forum.html')
	
def gallery(request):
    return render(request, 'mammoth/gallery.html', context={'all_patterns':Pattern.objects.all()})

def share_your_pattern(request):
    if request.method == 'POST':
        pattern_form = PatternForm(request.POST, request.FILES)

        if pattern_form.is_valid():
            if 'picture' in request.FILES:
                # user = request.user
                # pattern_form.picture = request.FILES['picture']
                # pattern_form.author = user
                # pattern_form.save()
                pattern = Pattern()
                pattern.title = pattern_form.cleaned_data['title']
                pattern.picture = request.FILES['picture']
                pattern.description = pattern_form.cleaned_data['description']
                pattern.author = request.user
                pattern.save()

            return render(request, 'mammoth/index.html', context={'pattern_uploaded':True})
        else:
            print(pattern_form.errors)
    else:
        pattern_form = PatternForm()
        user = request.user
    return render(request, 'mammoth/share_your_pattern.html', context={'pattern_form':pattern_form,'user':user})
	
def shop(request):
	return render(request, 'mammoth/shop.html')
	
def terms_and_conditions(request):
	return render(request, 'mammoth/terms_and_conditions.html')

def site_map(request):
	return render(request, 'mammoth/site_map.html')
	
def about_us(request):
    users = User.objects.all()
    context = {"users":users}
    return render(request, 'mammoth/about_us.html',context)

def contact_us(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			sender_name = form.cleaned_data['name']
			sender_email = form.cleaned_data['email']

			message = "{0} has sent you a new message:\n\n{1}".format(sender_name, form.cleaned_data['message'])
			send_mail('New Enquiry', message, sender_email, ['woollymammoth812@gmail.com'])
			return HttpResponse('Thanks for contacting us!')
	else:
		form = ContactForm()
		return render(request, 'mammoth/contact_us.html')
	
def faq(request):
	return render(request, 'mammoth/faq.html')

def knit_kit(request):
    return render(request, 'mammoth/knit_kit.html')


#==============================================================
#====================== Comment function ======================
#==============================================================
def submit_comment(request):
    user = request.user
    text = request.POST.get('text','').strip()
    rating = request.POST.get('rating', 0)
    pattern = Pattern.objects.get(id=int(int(request.POST.get('object_id',''))))
    
    # Create a comment model
    comment = Comment()
    comment.pattern = pattern
    comment.user = user
    comment.text = text
    comment.rating = rating
    comment.save()

    # Here: we can redirect the user to the page where they make comment
    # and if it cannot get previous page, it will redirect to mammoth:index
    refer = request.META.get("HTTP_REFERER","mammoth:index") 
        #for some special models (twittes? blog?) which might have comments for that model
    # , use this to show its comment
    # get all comment model : comments = Comment.objects.filter(object_id = pattern.pk )
    # and then return it to template page
    return redirect(refer)

# get current users
def get_current_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    # Query all logged in users based on id list
    return User.objects.filter(id__in=user_id_list)