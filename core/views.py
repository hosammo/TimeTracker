from django.shortcuts import render, redirect, get_object_or_404

from core.models import Client


def client_list(request):
    from core.models import Workspace
    clients = Client.objects.all()
    workspaces = Workspace.objects.all()
    return render(request, 'clients.html', {
        'clients': clients,
        'workspaces': workspaces
    })

def create_client(request):
    if request.method == 'POST':
        Client.objects.create(
            name=request.POST.get('name'),
            workspace_id=request.POST.get('workspace_id')
        )
    return redirect('client_list')
def update_client(request, client_id):
    from core.models import Client
    if request.method == 'POST':
        client = Client.objects.get(id=client_id)
        client.name = request.POST.get('name')
        client.save()
    return redirect('client_list')
