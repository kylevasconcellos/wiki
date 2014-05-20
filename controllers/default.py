# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
	if not session.counter:
		session.counter = 1
	else:
		session.counter += 1
	pages = db().select(db.pageWiki.id,db.pageWiki.title,orderby=db.pageWiki.title)
	return dict(pages=pages,counter=session.counter)

"""@auth.requires_login()"""
def create():
    """creates a new empty wiki page"""
    form = SQLFORM(db.pageWiki).process(next=URL('index'))
    return dict(form=form)

def show():
    """shows a wiki page"""
    this_page = db.pageWiki(request.args(0,cast=int)) or redirect(URL('index'))
    db.postWiki.page_id.default = this_page.id
    form = SQLFORM(db.postWiki).process()
    pagecomments = db(db.postWiki.page_id==this_page.id).select()
    return dict(pageWiki=this_page, comments=pagecomments, form=form)

"""@auth.requires_login()"""
def documents():
    """browser, edit all documents attached to a certain page"""
    page = db.pageWiki(request.args(0,cast=int)) or redirect(URL('index'))
    db.documentWiki.page_id.default = page.id
    db.documentWiki.page_id.writable = False
    grid = SQLFORM.grid(db.documentWiki.page_id==page.id,args=[page.id])
    return dict(page=page, grid=grid)
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def search():
    """an ajax wiki search page"""
    return dict(form=FORM(INPUT(_id='keyword',_name='keyword',
                                _onkeyup="ajax('callback',['keyword'], 'target');")), target_div=DIV(_id='target'))

def callback():
    """an ajax callback that returns a <ul> of links to wiki pages"""
    query = db.pageWiki.title.contains(request.vars.keyword)
    pages = db(query).select(orderby=db.pageWiki.title)
    links = [A(p.title, _href=URL('show',args=p.id)) for p in pages]
    return UL(*links)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
