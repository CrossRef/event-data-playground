import requests
import json
import itertools

# Some headline figures from Event Data Query API.
# Put together quickly and hackily!
# Produces Markdown output.

sources = ["wikipedia", "twitter", "newsfeed", "facebook", "crossref_datacite"]

date = "2016-08-22"
api_date_source = "http://query.api.eventdata.crossref.org/%(view)s/%(date)s/sources/%(source)s/events.json"
api_date_all = "http://query.api.eventdata.crossref.org/%(view)s/%(date)s/events.json"
top_n = 5

def print_json_indent(data):
  print()
  indent = "    "
  print(indent + json.dumps(data, indent=2).replace("\n", "\n" + indent)) 
  print()

def main_top_n_total():
  """Top N per source"""
  print("# Top %d Events per source by total" % top_n)
  for source in sources:
    print("## Source: %s" % source)
    url = api_date_source % {"source": source, "date": date, "view": "collected"}

    events = requests.get(url).json()['events']

    by_count = sorted(events, key=lambda event: event['total'], reverse=True)[:top_n]

    for event in by_count:
      print_json_indent(event)

def main_top_n_count():
  """Top N per source"""
  print("# Top %d DOIs per source by total" % top_n)
  for source in sources:
    print("## Source: %s" % source)
    url = api_date_source % {"source": source, "date": date, "view": "collected"}

    events = requests.get(url).json()['events']

    proj_obj = lambda event: event['obj_id']
    
    doi_events = ((doi, list(events)) for doi, events in itertools.groupby(sorted(events, key=proj_obj), key=proj_obj))
    doi_count_events = [(doi, len(events), events) for doi, events in doi_events]
    
    # sorted by number of events
    dois = sorted(doi_count_events, key=lambda x: x[1], reverse=True)

    for (doi, count, events) in dois[:top_n]:
      print("### %s" % doi)
      print("%d events" % count)
      for event in events[:top_n]:
        print_json_indent(event)
        


def main_source_diversity():
  """Return top N events ordered by the diversity of sources for the subject."""
  print("# DOIs that have events from more than one source.")
  url = api_date_all % {"date": date, "view": "collected"}
  events = requests.get(url).json()['events']

  # Group by DOI.
  for doi, doi_group in itertools.groupby(sorted(events, key=lambda event: event['obj_id']), lambda event: event['obj_id']):
    doi_group_list = list(doi_group)
    doi_group_size = len(doi_group_list)

    # We want DOIs that appear in 2 or more sources. Discard DOIs with less than 2 events.
    if doi_group_size < 2:
      continue

    proj_source = lambda event: event['source_id']
    source_groups = itertools.groupby(sorted(doi_group_list, key=proj_source), proj_source)

    per_source_groups = [(source,list(events)) for source,events in source_groups]

    num_sources = len(per_source_groups)

    # We want more than one distinct source type.
    if num_sources < 2:
      continue

    print("## %s" % doi)

    for source, group_events in per_source_groups:
      events_list = list(group_events)
      print("### Source: %s, %d events" % (source, len(events_list)))
      print("Event:")
      for ev in events_list:
        print_json_indent(ev)
        break

      print("\n")


main_top_n_total()
main_top_n_count()
main_source_diversity()
