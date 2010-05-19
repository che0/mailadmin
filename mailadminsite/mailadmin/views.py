# -*- coding: utf-8 -*-
import hashlib

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from mailadmin.models import VirtualDomains

@staff_member_required
def my_domains(request):
    if request.user.is_superuser:
        my_domains = VirtualDomains.objects.all()
    else:
        my_domains = request.user.virtualdomains_set.all()
    
    domain_list = {}
    for domain in my_domains.order_by('name'):
        domain_out = {}
        for user in domain.virtualusers_set.all():
            domain_out[user.user] = {'type': 'mailbox'}
        for alias in domain.virtualaliases_set.order_by('source'):
            if not alias.source in domain_out:
                domain_out[alias.source] = {'type': 'alias', 'destinations':[alias.destination]}
            elif domain_out[alias.source] == 'mailbox':
                domain_out[alias.source] = 'mailbox_alias_combo'
            elif domain_out[alias.source] == 'alias':
                domain_out[alias.source]['destinations'].append(alias.destination)
        domain_list[domain.name] = domain_out
    
    return render_to_response(u'admin/mailadmin/my_domains.html',
        {
            'domain_list': domain_list,
        }, RequestContext(request),
    )

class ChangePasswordForm(forms.Form):
    email = forms.EmailField(max_length=255)
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        def _hash_password(plaintext):
            m = hashlib.md5()
            m.update(plaintext)
            return m.hexdigest()
        cleaned_data = self.cleaned_data
        
        need_fields = ('email', 'old_password', 'new_password1', 'new_password2')
        for f in need_fields:
            if f not in cleaned_data:
                raise forms.ValidationError(u"You need to fill in everything")
        
        try:
            user, domain = cleaned_data['email'].split('@')
            pwhash = _hash_password(cleaned_data['old_password'])
            cleaned_data['user'] = VirtualDomains.objects.get(name=domain).virtualusers_set.get(user=user, password=pwhash)
        except:
            raise forms.ValidationError(u"Old password does not match")
        if cleaned_data['new_password1'] != cleaned_data['new_password2']:
            raise forms.ValidationError(u"New password does not match")
        cleaned_data['new_hash'] = _hash_password(cleaned_data['new_password1'])
        return cleaned_data


def change_mailbox_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            user.password = form.cleaned_data['new_hash']
            user.save()
            return HttpResponseRedirect(reverse(change_mailbox_password_ok))
    else:
        form = ChangePasswordForm()
    
    return render_to_response('mailadmin/change_password.html', {
        'form': form,
    }, RequestContext(request))


def change_mailbox_password_ok(request):
    return render_to_response('mailadmin/change_password_ok.html', {}, RequestContext(request))
