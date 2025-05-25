# Enhanced core/views.py - PRESERVING ALL EXISTING + ADDING NEW FEATURES

from django.shortcuts import render, redirect, get_object_or_404
from core.models import Client, Workspace


def client_list(request):
    # PRESERVE: All existing functionality exactly as is
    from core.models import Workspace
    clients = Client.objects.select_related('workspace').all()  # ADD: Optimize query
    workspaces = Workspace.objects.all()

    # ADD: Statistics for enhanced UI
    total_clients = clients.count()
    clients_with_email = clients.exclude(email__in=['', None]).count()
    clients_with_company = clients.exclude(company__in=['', None]).count()

    return render(request, 'clients.html', {
        'clients': clients,  # PRESERVE: Existing
        'workspaces': workspaces,  # PRESERVE: Existing
        # ADD: New context for enhanced UI
        'total_clients': total_clients,
        'clients_with_email': clients_with_email,
        'clients_with_company': clients_with_company,
    })


def create_client(request):
    # ENHANCE: Add support for all fields while preserving existing logic
    if request.method == 'POST':
        # Validate required fields (preserve existing validation)
        name = request.POST.get('name')
        workspace_id = request.POST.get('workspace_id')

        if not name or not workspace_id:
            # ADD: Better error handling
            from django.contrib import messages
            messages.error(request, 'Name and Workspace are required fields.')
            return redirect('client_list')

        # PRESERVE: Existing creation logic + ADD: New fields
        Client.objects.create(
            name=name,  # PRESERVE: Existing
            workspace_id=workspace_id,  # PRESERVE: Existing
            email=request.POST.get('email', ''),  # ADD: New field
            company=request.POST.get('company', ''),  # ADD: New field
        )

        # ADD: Success message
        from django.contrib import messages
        messages.success(request, f'Client "{name}" created successfully!')

    return redirect('client_list')  # PRESERVE: Existing redirect


def update_client(request, client_id):
    # ENHANCE: Support all fields while preserving existing functionality
    from core.models import Client
    if request.method == 'POST':
        try:
            client = Client.objects.get(id=client_id)

            # PRESERVE: Existing field update
            name = request.POST.get('name')
            if name:
                client.name = name

            # ADD: Enhanced field updates with validation
            if 'email' in request.POST:
                email = request.POST.get('email', '').strip()
                if email and '@' not in email:
                    from django.contrib import messages
                    messages.error(request, 'Please enter a valid email address.')
                    return redirect('client_list')
                client.email = email

            if 'company' in request.POST:
                client.company = request.POST.get('company', '').strip()

            if 'workspace_id' in request.POST:
                workspace_id = request.POST.get('workspace_id')
                if workspace_id:
                    client.workspace_id = workspace_id

            client.save()

            # ADD: Success message
            from django.contrib import messages
            messages.success(request, f'Client "{client.name}" updated successfully!')

        except Client.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'Client not found.')

    return redirect('client_list')  # PRESERVE: Existing redirect


# ADD: New function for delete functionality (required by enhanced UI)
def delete_client(request, client_id):
    if request.method == 'POST':
        try:
            client = get_object_or_404(Client, id=client_id)
            client_name = client.name

            # Check if client has related projects (prevent accidental deletion)
            from projects.models import Project
            related_projects = Project.objects.filter(client=client).count()

            if related_projects > 0:
                from django.contrib import messages
                messages.warning(request,
                                 f'Cannot delete "{client_name}" - client has {related_projects} related project(s). Archive projects first.')
            else:
                client.delete()
                from django.contrib import messages
                messages.success(request, f'Client "{client_name}" deleted successfully!')

        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error deleting client: {str(e)}')

    return redirect('client_list')