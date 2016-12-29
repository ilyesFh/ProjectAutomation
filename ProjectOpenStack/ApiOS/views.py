import keystoneclient.v2_0.client as ksclient
from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client as nova_client
import glanceclient.v2.client as glance_client
from django.shortcuts import render
from django.shortcuts import redirect
import time
from .forms import SingUpForm


# Create your views here.




def singUp(request):


    title="Authentication"

    form=SingUpForm(request.POST or None)

    context ={
        "title":title,
        "form":form,
            }

    if form.is_valid():
        try:
            name=form.cleaned_data['name']
            tenant=form.cleaned_data['tenant']
            password=form.cleaned_data['password']
            keystone = ksclient.Client(auth_url="http://192.168.38.131:35357/v2.0",
                           username=name,
                           password=password,
                           tenant_name=tenant)

            tok = keystone.auth_token


            request.session['tok']=tok
            request.session['name']=name
            request.session['tenant'] =tenant
            request.session['password'] =password
            return redirect('/home')

        except:
            return render(request, "SingUp.html", context)

    return render(request, "SingUp.html", context)

def home(request):

    try:
        token = request.session['tok']
        name = request.session['name']
        tenant = request.session['tenant']
        password = request.session['password']
        gc = glance_client.Client(endpoint='http://192.168.38.131:9292',token=token)
        auth = v2.Password(auth_url="http://192.168.38.131:5000/v2.0",
                       username=name,
                       password=password,
                       tenant_name=tenant)  # the admin's tenant

        auth_session = session.Session(auth=auth)
        nova = nova_client.Client(2, session=auth_session)

        fl = nova.flavors.list()

    # im=gc.images.get(image_id='7247110f-858b-46b5-a237-7fc08148c931')
        im = gc.images.list()
        imag = []
        for img in im:
            imag = imag + [(img.name, img.id)]
        if request.method == "POST":
            idim = request.POST['imm']
            flv = request.POST['flav']
            name = request.POST['na']

            # nova.keypairs.create(name="mykey")
            image = nova.images.find(name=idim)
            flavor = nova.flavors.find(name=flv)
            instance = nova.servers.create(name=name, image=image, flavor=flavor, key_name="mykey",
                                       availability_zone="nova")
            status = instance.status
            while status == 'BUILD':
                time.sleep(3)
                # Retrieve the instance again so the status field updates
                instance = nova.servers.get(instance.id)
                status = instance.status

                # Poll at 5 second intervals, until the status is no longer 'BUILD'

                return redirect('/list')
    except:
        return render(request, "Home.html", {"resp":imag, "fl": fl,"user":tenant})
    return render(request, "Home.html", {"resp":imag, "fl": fl,"user":tenant})


def list(request):


    name = request.session['name']
    tenant = request.session['tenant']
    password = request.session['password']

    auth = v2.Password(auth_url="http://192.168.38.131:5000/v2.0",
                        username=name,
                        password=password,
                        tenant_name=tenant)  # the admin's tenant

    auth_session = session.Session(auth=auth)
    nova = nova_client.Client(2, session=auth_session)
    instances=nova.servers.list()

    return render(request, "List.html", {"inst": instances,"user":tenant})

