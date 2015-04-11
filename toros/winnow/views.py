from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from winnow.forms import RankingForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from winnow.models import TransientCandidate, Ranking, UserProfile
from django.contrib.auth import authenticate, login, logout


def index(request):
    return render(request, 'winnow/index.html', {'page_index': 'selected'})

@login_required
def rank(request):
    if request.method == "POST":
        form = RankingForm(request.POST)
        
        if form.is_valid():
            if request.user.is_authenticated():
                r = form.save(commit=False)
                r.ranker = UserProfile.objects.get(user=request.user)
                tc_id = int(request.POST.get('tc_id'))
                r.trans_candidate = TransientCandidate.objects.get(pk=tc_id)
                r.save()
            return index(request)
        else:
            print form.errors
            tc_id = int(request.POST.get('tc_id'))
    else:
        try:
            #Fetch any tc not ranked yet
            tc = TransientCandidate.objects.exclude(ranking=Ranking.objects.all())[0]
        except IndexError:
            #Fetch any tc not ranked by the current user
            try:
                currentUser = UserProfile.objects.get(user=request.user)
                tc = TransientCandidate.objects.exclude(ranking=Ranking.objects.filter(ranker=currentUser))[0]
            except IndexError:
                tc = None
        
        if tc is None:
            tc_id = -1
        else:
            tc_id = tc.id
        
        form = RankingForm()
    
    return render(request, 'winnow/rank.html', {'form': form, 'page_rank': 'selected', 'tc_id' : tc_id})


def about(request):
    return render(request, 'winnow/about.html', {'page_about': 'selected'})
    
def thumb(request, trans_candidate_id):
    
    tc = TransientCandidate.objects.get(pk=trans_candidate_id)
    
    from astropy.io import fits
    from toros.settings import ASTRO_IMAGE_DIR
    from os import path
    image_data = fits.getdata(path.join(ASTRO_IMAGE_DIR, tc.filename))
    thumb_arr = image_data[tc.y_pix - tc.height: tc.y_pix + tc.height, tc.x_pix - tc.width: tc.x_pix + tc.width]

    #import numpy as np
    #thumb_arr = np.random.random((10,10))
    
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(5,5))
    plt.imshow(thumb_arr, interpolation='none')
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close()
    return response


def register(request):
    registered = False

    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Print form errors if any to the terminal
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'winnow/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/training/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'winnow/login.html', {})
        
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/training/')