# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class VirtualDomains(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, help_text=u'Virtual domain name, such as <code>example.com</code>')
    admin = models.ManyToManyField(User, db_table=u'virtual_domain_admins')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = u'Virtual domains'
        db_table = u'virtual_domains'

class VirtualAliases(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.ForeignKey(VirtualDomains, help_text=u'Domain on which the alias is going to live')
    source = models.CharField(max_length=120, help_text=u'Alias username; e.g. the part before <code>@</code> in address')
    destination = models.CharField(max_length=240, help_text=u'Full destination e-mail address, such as <code>fans@tokiohotel.de</code>. If you want to forward to multiple destinations, add more alias items for the same source address.')
    def __unicode__(self):
        return '%s@%s -> %s' % (self.source, self.domain.name, self.destination)
    def full_source(self):
        return '%s@%s' % (self.source, self.domain.name)
    class Meta:
        verbose_name_plural = u'Virtual aliases'
        db_table = u'virtual_aliases'

class VirtualUsers(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.ForeignKey(VirtualDomains, help_text=u'Domain where is the mailbox going to live')
    user = models.CharField(unique=True, max_length=120, help_text=u'Mailbox username; e.g. the part before <code>@</code> in address')
    password = models.CharField(max_length=96, help_text=u'MD5 hex digest of the password')
    def __unicode__(self):
        return '%s@%s' % (self.user, self.domain.name)
    class Meta:
        verbose_name_plural = u'Virtual users'
        db_table = u'virtual_users'

