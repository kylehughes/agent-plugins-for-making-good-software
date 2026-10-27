# Explain Lumen's search view

## Request

Write a short explanation for team leads who use Lumen but do not operate it. They keep treating a search result as proof of the current record, and treating a missing search result as proof a record was deleted. Help them reason through what they are seeing and where to check. Use the product notes below; do not turn this into an operator runbook.

## Factual source

Lumen tracks equipment requests. Each request has a stable request number. The request page reads the current stored record. Search reads a separate search view built from changes to stored records. Search normally catches up within two minutes, but no maximum delay is guaranteed. A backlog can make it take longer. Refreshing the browser reruns the search against the same possibly stale view; it does not force an update. The product has no user control for forcing a search update.

Creating or editing a request updates the stored record before the search view. Closing a request changes its stored status to Closed; it does not delete it. Search defaults to open requests. Selecting Include closed changes that filter, but cannot fix a stale search view. Deleting a request removes its stored record; an old search result can remain temporarily. Opening that old result shows `Request not found`. `Request not found` can also mean the user lacks permission; team leads cannot distinguish those reasons from that screen. A request number by itself does not prove access.

If you have a request link, open it to check the current values you are allowed to see. If you only have a request number, use Open by number; it reads the stored record subject to the same permissions. When the page opens, its status is authoritative for that request at the time the page was loaded; another edit can occur later. Team leads cannot diagnose search backlog or restore deleted records. If the record page and search still disagree after the usual two-minute interval, send the request number and observed times to the service desk. Do not send private request contents. The service desk checks backlog and access. There is no published recovery time.

No starting document exists. This is the complete product evidence for the explanation.
