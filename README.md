mini-sync
===================

Python/SQLAlchemy and AngularJS bindings for a non-concurrent, DRY, fairly RESTful client-server object synchronization pattern. An experiment in minimalist web application architecture.

What does mini-sync do?
-----------

Mini-sync eliminates mapper-layer profileration by abstracting away useless mapper layers between your database API and your web application client. It implements an object synchronization pattern, described in more detail below.

Why the object sychronization pattern?
-----------
The dogma in web application architecture implies that we need several layers of abstraction between the source of truth (usually a database) and the client. This dogma says that writing a high-level resource-oriented data access layer (or DAL) over a database API or object-relational mapper helps:

-> Improve security by compartmentalizing access to resources, and

-> Keep business logic in one place, for easy updates to that logic.

The above points made some sense and had a little merit back when the best way to write a client was by linking sets of pages with HTML forms. Now, thin clients are in again (for good reason, including increased download speeds, a network stack optimized for medium-sized downloads, and browser capabilities and APIs).

Resource-oriented DALs do not improve security. Specifying permissions on resources can decrease the attack surface, but one does not need to put layer after layer of mappers between the database API and the client in order to this achieve attack surface reduction.

How mini-sync works
------------

Clients specify resources in the following way:

	{"serverMapperClassName": "clientSideModelObjectName"}
	resourcesProvider.setResources(resourcesObj); // AngularJS example
	
For the read operation, servers send flattened data objects as JSON. The data objects have keys and values. A key may be a string path through a mapper object (like "user.contact_info.email_address" or "user.addresses.5.postal_code", if the server mapper class name were "User") or the name of a property on the root object. A value may be a string or number.

The client processes server responses to read operations, and binds the read data to client-side models.

Clients specify a primary key field or fields, and use dirty-checking to compile a list of updates to client-side models. Clients also specify a 'trigger event' on the DOM, which, when fired, will cause initiate the client-server object sync.

When the trigger event fires, the server receives a diff of the original objects (i.e. the values at read-time) and the new objects. If the primary key field is specified, the object is updated. If a delete flag is specified, the object is deleted. If no primary key field is specified, the object is created.

The server unflattens the input and attempts to automagically map input fields to your database API or object-relational mapper. Mini-sync supports related objects of any depth for create, read, update and delete operations.

Mini-sync's bindings for AngularJS and SQLAlchemy handle all of the above for you. You don't have to do dirty checking, serialization, deserialization, etc.

Example usage (Flask):

	from flask import request
	from osp import SyncObject
	import json
	
	data = json.loads(request.data)
	for resource_name, mapper_obj_dict in data.iteritems():
		mapper_module_name, mapper_class_name = resource_name.split('.')
 		mapper_module = getattr(core, mapper_module_name)
		mapper_class = getattr(mapper_module, mapper_class_name)
		SyncObject(mapper_class, mapper_obj_dict)

Eventually, the server library for mini-sync will support hooks for merge strategies. This will help make mini-sync  safer for use in concurrent environments (those in which two or more clients may access and change resources in overlapping timeframes).

Benefits
------------
Instead of hundreds of lines of DAL code, DAL tests, client-side coding, etc, you just have a few lines of configuration, a create/update event hook, a delete hook, and a line of HTML.

JavaScript (AngularJS):

	resourcesProvider.setResource({"serverUserMapper": "angularUserModel"});
	resourcesProvider.setCuHook(myEvent);
	resourcesProvider.setOspEndpoint('https://myserver.ext/ospEndpoint')
	
HTML (with AngularJS bindings):

	<textarea name="profile_text" ng-model="angularUserModel.profile_text"></textarea>
	

Principles
------------

-> Mapper layer proliferation is usually bad: Writing mapper layers is one of the biggest pains in modern web application development. So Don't Repeat Yourself with respect to mapper layers.

-> Data access layers are not security devices. The client can be trusted to create, read update and delete certain resources if it can be authorized, authenticated, and permissioned with respect to the resource type or instance being manipulated.

-> Homogenous exception handling: The server should be a black box that will safely accept any input, return a standardized response if that input is invalid, and return a standardized response if that input is valid.

Writing Create, Read, Update and Delete applications should be this easy.

License
------------

The MIT License (MIT)
Copyright &copy; 2013 Zach Dexter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.