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