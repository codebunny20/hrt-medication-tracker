import json
import os

class DataManager:
    def __init__(self, data_directory=None):
        if data_directory is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            data_directory = os.path.join(base_dir, "data")
        self.data_directory = data_directory
        self.hrt_entries_file = os.path.join(data_directory, 'hrt_entries.json')
        self.hrt_resources_file = os.path.join(data_directory, 'hrt_resources.json')
        self.symptoms_file = os.path.join(data_directory, 'symptoms.json')
        # NEW: grouped symptom entries (similar to HRT log entries)
        self.symptom_entries_file = os.path.join(data_directory, 'symptom_entries.json')

    def _load_list_or_wrapped(self, path, list_key):
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and list_key in data:
            return data[list_key]
        if isinstance(data, list):
            return data
        return []

    def _save_list_or_wrapped(self, path, list_key, items):
        wrapped = {list_key: items}
        with open(path, "w") as f:
            json.dump(wrapped, f, indent=4)

    # --- internal helpers ------------------------------------------------
    def _ensure_ids(self, items, file_path, id_prefix: str):
        """Ensure each dict in 'items' has an 'id'. Mutates list and returns it."""
        if not items:
            return items
        changed = False
        file_mtime = int(os.path.getmtime(file_path)) if os.path.exists(file_path) else 0
        for idx, e in enumerate(items):
            if isinstance(e, dict) and "id" not in e:
                e["id"] = f"{id_prefix}-{file_mtime}-{idx}"
                changed = True
        if changed:
            # caller will persist using appropriate save_* method
            pass
        return items

    def load_hrt_entries(self):
        """Return list of HRT entries.

        Each entry may be a simple dict like:
          {"entry": "text", "timestamp": "..."}
        or a richer dict with fields such as:
          {"id": "...", "title": "...", "date": "YYYY-MM-DD", "time": "HH:MM",
           "mood": "...", "symptoms": "...", "notes": "...",
           "medications": [...], "timestamp": "..."}
        Ensures that each entry dict has an 'id' field for internal use.
        """
        entries = self._load_list_or_wrapped(self.hrt_entries_file, "entries")
        # ensure each dict entry has an id; non-dict entries are left as-is
        entries = self._ensure_ids(entries, self.hrt_entries_file, "hrt")
        # if we had to add ids, persist them
        self.save_hrt_entries(entries)
        return entries

    def save_hrt_entries(self, entries):
        self._save_list_or_wrapped(self.hrt_entries_file, "entries", entries)

    def load_hrt_resources(self):
        """Load resources as a list of dicts with stable shape.

        Each resource dict will have at least:
          {"name": str, "link": str, "description": str, "tags": list[str]}
        Legacy plain strings or partial dicts are normalized.
        """
        raw = self._load_list_or_wrapped(self.hrt_resources_file, "resources")

        normalized = []
        for item in raw:
            if isinstance(item, dict):
                name = str(item.get("name") or "").strip()
                link = str(item.get("link") or "").strip()
                description = str(item.get("description") or "").strip()
                tags_val = item.get("tags", [])
                # normalize tags to list[str]
                if isinstance(tags_val, str):
                    tags = [t.strip() for t in tags_val.split(",") if t.strip()]
                elif isinstance(tags_val, list):
                    tags = [str(t).strip() for t in tags_val if str(t).strip()]
                else:
                    tags = []
            else:
                # legacy plain string
                name = str(item).strip()
                link = ""
                description = ""
                tags = []

            normalized.append(
                {
                    "name": name,
                    "link": link,
                    "description": description,
                    "tags": tags,
                }
            )

        # persist normalized structure back to disk
        self.save_hrt_resources(normalized)
        return normalized

    def save_hrt_resources(self, resources):
        """Save resources ensuring they are a list of dicts with canonical keys."""
        safe_resources = []
        for r in resources:
            if isinstance(r, dict):
                name = str(r.get("name") or "").strip()
                link = str(r.get("link") or "").strip()
                description = str(r.get("description") or "").strip()
                tags_val = r.get("tags", [])
                if isinstance(tags_val, str):
                    tags = [t.strip() for t in tags_val.split(",") if t.strip()]
                elif isinstance(tags_val, list):
                    tags = [str(t).strip() for t in tags_val if str(t).strip()]
                else:
                    tags = []
            else:
                name = str(r).strip()
                link = ""
                description = ""
                tags = []

            safe_resources.append(
                {
                    "name": name,
                    "link": link,
                    "description": description,
                    "tags": tags,
                }
            )

        self._save_list_or_wrapped(self.hrt_resources_file, "resources", safe_resources)

    def load_symptoms(self):
        return self._load_list_or_wrapped(self.symptoms_file, "symptoms")

    def save_symptoms(self, symptoms):
        self._save_list_or_wrapped(self.symptoms_file, "symptoms", symptoms)

    # --- NEW: grouped symptom entries (history-style) --------------------
    def load_symptom_entries(self):
        """Return list of grouped symptom entries (similar to HRT log entries).

        Each entry is expected to be a dict, for example:
          {
            "id": "...",
            "kind": "symptom",
            "title": "Symptoms",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "symptoms": ["Fatigue", "Nausea"],
            "notes": "...optional free text...",
            "timestamp": "ISO8601"
          }
        """
        entries = self._load_list_or_wrapped(self.symptom_entries_file, "entries")
        entries = self._ensure_ids(entries, self.symptom_entries_file, "sym")
        self.save_symptom_entries(entries)
        return entries

    def save_symptom_entries(self, entries):
        self._save_list_or_wrapped(self.symptom_entries_file, "entries", entries)

    def delete_entry_by_id(self, entry_id: str) -> bool:
        """Delete a single entry by its 'id'. Returns True if something was deleted.

        This checks both HRT entries and symptom entries.
        """
        # HRT entries
        entries = self.load_hrt_entries()
        new_entries = [e for e in entries if not (isinstance(e, dict) and e.get("id") == entry_id)]
        if len(new_entries) != len(entries):
            self.save_hrt_entries(new_entries)
            return True

        # Symptom entries
        s_entries = self.load_symptom_entries()
        new_s_entries = [e for e in s_entries if not (isinstance(e, dict) and e.get("id") == entry_id)]
        if len(new_s_entries) != len(s_entries):
            self.save_symptom_entries(new_s_entries)
            return True

        return False

    def duplicate_entry_by_id(self, entry_id: str) -> bool:
        """Duplicate an entry by id (HRT or symptom), assigning a new id and timestamp."""
        from datetime import datetime  # local import to avoid unused at module import

        # HRT entries
        entries = self.load_hrt_entries()
        for e in entries:
            if isinstance(e, dict) and e.get("id") == entry_id:
                clone = json.loads(json.dumps(e))  # deep copy
                now = datetime.now()
                clone["timestamp"] = now.isoformat(timespec="seconds")
                clone["id"] = f"hrt-{now.strftime('%Y%m%d%H%M%S')}-{len(entries)}"
                entries.append(clone)
                self.save_hrt_entries(entries)
                return True

        # Symptom entries
        s_entries = self.load_symptom_entries()
        for e in s_entries:
            if isinstance(e, dict) and e.get("id") == entry_id:
                clone = json.loads(json.dumps(e))
                now = datetime.now()
                clone["timestamp"] = now.isoformat(timespec="seconds")
                clone["id"] = f"sym-{now.strftime('%Y%m%d%H%M%S')}-{len(s_entries)}"
                s_entries.append(clone)
                self.save_symptom_entries(s_entries)
                return True

        return False