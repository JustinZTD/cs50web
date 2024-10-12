import random
from django.shortcuts import render, redirect
import markdown2
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry_content = util.get_entry(title)
    if entry_content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found"
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(entry_content),
            "title": title
        })

def search(request):
    if request.method == "POST":
        query = request.POST["q"]
        if util.get_entry(query):
            return redirect("entry", title=query)
        matches = []
        for entry in util.list_entries():
            if query.lower() in entry.lower():
                matches.append(entry)
        if matches:
            return render(request, "encyclopedia/index.html", {
                "entries": matches
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "message": "No matches found"
            })
        
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        contents = request.POST["contents"]
        if util.get_entry(title):
            return render(request, "encyclopedia/error.html", {
                "message": "Page already exists"
            })
        else:
            util.save_entry(title, contents)
            return redirect("entry", title=title)
    return render(request, "encyclopedia/create.html")

def random_page(request):
    entries = util.list_entries()
    title = entries[random.randint(0, len(entries) - 1)]
    return redirect("entry", title=title)