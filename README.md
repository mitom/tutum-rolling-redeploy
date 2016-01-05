# Simple rolling deploy for tutum

**Disclaimer:** Use this at your own risk, any issues or harm caused by this script is your own responsibility.

The aim is to get 0 downtime updates.

It will go through all *running* and *starting* (at the time when the script is ran) containers of a service and redeploy them one by one.
The next container will be issued a redeploy once a *new* container comes up, meaning if one was *starting* when the script was run
 and came up, it will just wait for its' turn and be redeployed, since it is possible it was crashing. If a container that
 wasn't in the list comes up, it will trigger the redeploy for the next one in line, because we have 1 extra one running now, so even if
 the previous one we issued the redeploy to isn't finished yet, we should be safe.

I'd recommend using this on a service that is behind a load balancer that watches for tutum container states rather than just reachability.
Check out my [nginx load balancer for tutum](https://hub.docker.com/r/mitom/tutum-nginx-loadbalancer/) or use HAproxy if you don't want to bother with nginx.

## Requirements

The only requirements are python and `tutum-python` (get it with pip).

## Usage

The script runs on env variables:
* `TUTUM_USER` - the username in tutum
* `TUTUM_APIKEY` - an api key for tutum
* `TUTUM_AUTH` - the auth header for tutum, handy if this runs in a docker container in tutum with full access
* `TUTUM_SERVICE` - the uuid of the service to redeploy
* `TUTUM_GRACE_PERIOD` - a number in seconds to wait before issuing the next redeploy after a container comes up. Defaults to 0

Either `TUTUM_USER` AND `TUTUM_APIKEY` are needed OR `TUTUM_AUTH`, but `TUTUM_AUTH` will be preferred if all are present.

## Redeploying in bulk

When you have more than a few containers in a service it becomes pretty long to roll them over one by one and wait for them to revive.
In this case, you might want to set `TUTUM_REDEPLOY_STEP` (defaults to 1), either to a number, `half` or `service`.

`half` will send half of your containers down at once and keep sending new ones down as they come up.
`service` will issue a service redeploy instead of sending it to all the containers individually, so the grace period doesn't apply here.

For example, say you have 10 containers and let's say it takes 10 seconds to redeploy one, so you set redeploy step to be `half`.
You start the process and the script will send 5 of those containers into redeploy. The requests are not sent in parallel as
they wait for tutum's acknowledgement, so there is some delay between those, but in 10-some seconds you should have 5
new containers up, and as soon as one comes up an other (not yet redeployed) one goes down for redeploy.

It would look something like this on a timeline:
(`-` is 1s on running, `_` is 1 second of being in redeployment, `|` is done)

The following examples make the assumption:
* grace period is 0
* it takes flat 1s to send the request for the redeploy and receive a response
* it takes flat 10s to redeploy a container

````
-_________|
--_________|
---_________|
----_________|
-----_________|
-----------_________|
------------_________|
-------------_________|
--------------_________|
---------------_________|
|0                      |25
````

If you were to roll those with a step of 1, it would look something like this:
````
-_________|
-----------_________|
---------------------_________|
-------------------------------_________|
-----------------------------------------_________|
---------------------------------------------------_________|
-------------------------------------------------------------_________|
-----------------------------------------------------------------------_________|
---------------------------------------------------------------------------------_________|
-------------------------------------------------------------------------------------------_________|
|0                      |25                                                                         |101
````

Using `service` would be:
````
-_________|
-_________|
-_________|
-_________|
-_________|
-_________|
-_________|
-_________|
-_________|
-_________|
|0        |11
````
This is pretty much the same as pressing the button in the web interface.