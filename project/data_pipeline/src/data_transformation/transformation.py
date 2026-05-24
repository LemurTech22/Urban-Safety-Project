
"""
Goal is to cluster all values based on location and find hotspots where accidents occur.
"""
import pandas as pd

class Transformation:
    def __init__(self,df: pd.DataFrame):  
        self.df = df 
        self.DROP_COLS = [
            "report_number",            
            "local_case_number",        
            "agency_name",              
            "person_id",                # PII — UUID identifying a person
            "vehicle_id",               
            "geolocation",              
            "related_non_motorist",     
            "non_motorist_substance_abuse",
        ]

        self.WEATHER_MAP = {
            "CLEAR":            "Clear",
            "clear":            "Clear",
            "CLOUDY":           "Cloudy",
            "cloudy":           "Cloudy",
            "RAIN":             "Rain",
            "rain":             "Rain",
            "SNOW":             "Snow",
            "snow":             "Snow",
            "ICE":              "Ice",
            "ice":              "Ice",
            "ICE/FROST":        "Ice",
            "BLOWING SNOW":     "Snow",
            "SLEET/HAIL":       "Sleet",
            "FOG/SMOG/SMOKE":   "Fog",
            "SEVERE WINDS":     "Severe Winds",
            "N/A":              "Unknown",
            "OTHER":            "Unknown",
            "UNKNOWN":          "Unknown",
        }

        self.SURFACE_MAP = {
            "DRY":          "Dry",
            "dry":          "Dry",
            "WET":          "Wet",
            "wet":          "Wet",
            "ICE":          "Ice",
            "ice":          "Ice",
            "ICE/FROST":    "Ice",
            "SNOW":         "Snow",
            "snow":         "Snow",
            "SLUSH":        "Slush",
            "SAND/MUD":     "Sand/Mud",
            "WATER":        "Wet",
            "N/A":          "Unknown",
            "OTHER":        "Unknown",
            "UNKNOWN":      "Unknown",
        }

        self.LIGHT_MAP = {
            "DAYLIGHT":         "Daylight",
            "Daylight":         "Daylight",
            "DARK":             "Dark",
            "DARK LIGHTS ON":   "Dark — Lights On",
            "DARK NO LIGHTS":   "Dark — No Lights",
            "DAWN":             "Dawn",
            "DUSK":             "Dusk",
            "OTHER":            "Unknown",
            "UNKNOWN":          "Unknown",
        }

    def standarize_data(self):
        if "weather" in self.df.columns:
            self.df["weather"] = (
                self.df["weather"].str.strip()
                .map(self.WEATHER_MAP)
                .fillna(self.df["weather"].str.strip().str.title())
            )
        if "surface_condition" in self.df.columns:
            self.df["surface_condition"] =(
                self.df["surface_condition"].str.strip()
                .map(self.SURFACE_MAP)
                .fillna(self.df["surface_condition"].str.strip().str.title())
            )

        if "light" in self.df.columns:
            self.df["light"] = (
                self.df["light"].str.strip()
                .map(self.LIGHT_MAP)
                .fillna(self.df["light"].str.strip().str.title())
            )

        str_cols = self.df.select_dtypes(include="object").columns
        self.df[str_cols] = self.df[str_cols].apply(lambda col: col.str.strip())
        
    def cast_types(self):

        # datetime
        self.df["crash_date_time"] = pd.to_datetime(
            self.df["crash_date_time"], errors="coerce"
        )

        # extract useful time parts for analysis
        self.df["crash_year"]    = self.df["crash_date_time"].dt.year
        self.df["crash_month"]   = self.df["crash_date_time"].dt.month
        self.df["crash_hour"]    = self.df["crash_date_time"].dt.hour
        self.df["crash_dow"]     = self.df["crash_date_time"].dt.day_name()

        # numeric
        self.df["latitude"]    = pd.to_numeric(self.df["latitude"],    errors="coerce")
        self.df["longitude"]   = pd.to_numeric(self.df["longitude"],   errors="coerce")
        self.df["speed_limit"] = pd.to_numeric(self.df["speed_limit"], errors="coerce").astype("Int64")
        self.df["vehicle_year"]= pd.to_numeric(self.df["vehicle_year"],errors="coerce").astype("Int64")

        # boolean-like
        self.df["driver_at_fault"]    = self.df["driver_at_fault"].map({"Yes": True, "No": False})
        self.df["driverless_vehicle"] = self.df["driverless_vehicle"].map({"Yes": True, "No": False})
        self.df["parked_vehicle"]     = self.df["parked_vehicle"].map({"Yes": True, "No": False})
    
    def drop_columns(self):
        cols_to_drop= [c for c in self.DROP_COLS if c in self.df.columns]
        self.df = self.df.drop(columns=cols_to_drop)

    def flag_dui(self):

        if "driver_substance_abuse" in self.df.columns:
            self.df["dui_flag"] = self.df["driver_substance_abuse"].str.contains(
                "Alcohol|Drug|Cannabis|Medication",
                case=False,
                na=False
            )

    def transform_to_silver(self):

        print(f"Starting silver transform — {len(self.df)} rows, {len(self.df.columns)} cols")

        self.drop_columns()
        print(f"  ✓ Dropped metadata columns — {len(self.df.columns)} cols remaining")

        self.standarize_data()
        print(f"  ✓ Standardized categoricals")

        self.cast_types()
        print(f"  ✓ Cast types — datetime, numeric, boolean")

        self.flag_dui()
        print(f"  ✓ DUI flag added — {self.df['dui_flag'].sum()} flagged records")

        # drop rows with null lat/lon — can't do hotspot analysis without coords
        before = len(self.df)
        self.df = self.df.dropna(subset=["latitude", "longitude"])
        dropped = before - len(self.df)
        if dropped > 0:
            print(f"  ✓ Dropped {dropped} rows with null coordinates")

        print(f"Silver transform complete — {len(self.df)} rows, {len(self.df.columns)} cols")
        return self.df

