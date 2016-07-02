from django.shortcuts import render
from django.http import HttpResponse

from scrapy.cmdline import execute

# Create your views here.
def index(request):
  return HttpResponse("Hello World!")

def postList(request, uid):
  execute(("scrapy runspider crawler/crawler.py -a uid=%s" % uid).split())
  return HttpResponse("The user id is: %s" % uid)
