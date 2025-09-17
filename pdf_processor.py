import PyPDF2
import pdfplumber
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json

@dataclass
class TestResult:
    name: str
    value: str
    unit: str = ""
    reference_range: str = ""
    status: str = ""

@dataclass
class PatientReport:
    registration_number: Optional[str] = None
    patient_name: Optional[str] = None
    age: Optional[str] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    collection_date: Optional[str] = None
    reporting_date: Optional[str] = None
    referring_doctor: Optional[str] = None
    location: Optional[str] = None
    lab_name: Optional[str] = None
    pathologist: Optional[str] = None
    
    hematology_tests: List[TestResult] = field(default_factory=list)
    biochemistry_tests: List[TestResult] = field(default_factory=list)
    serology_tests: List[TestResult] = field(default_factory=list)
    clinical_pathology_tests: List[TestResult] = field(default_factory=list)
    
    blood_group: Optional[str] = None
    rh_type: Optional[str] = None
    peripheral_smear_findings: List[str] = field(default_factory=list)
    clinical_notes: List[str] = field(default_factory=list)

class PathologyReportExtractor:
    def __init__(self):
        self.current_patient = None
        self.all_patients = []
        
        self.test_reference_data = {
            "HEMOGLOBIN": {
                "ranges": {"normal_min": 12.0, "normal_max": 16.0, "low": 12.0},
                "meaning": "Hemoglobin carries oxygen in your blood. Low levels can cause fatigue and anemia.",
                "tips": "Eat iron-rich foods like spinach, beetroot, and jaggery. Combine with Vitamin C foods like citrus fruits."
            },
            "Total RBC Count": {
                "ranges": {"normal_min": 4.5, "normal_max": 5.5, "low": 4.5},
                "meaning": "Red blood cells carry oxygen throughout your body.",
                "tips": "Maintain adequate iron, B12, and folate intake through green vegetables and lean meats."
            },
            "H.CT": {
                "ranges": {"normal_min": 36.0, "normal_max": 46.0, "low": 36.0},
                "meaning": "Hematocrit shows the percentage of blood made up of red blood cells.",
                "tips": "Stay hydrated and maintain a balanced diet rich in iron."
            },
            "M.C.V": {
                "ranges": {"normal_min": 80.0, "normal_max": 100.0, "low": 80.0},
                "meaning": "MCV indicates the average size of your red blood cells.",
                "tips": "Ensure adequate B12 and folate intake through fortified cereals and leafy greens."
            },
            "Total WBC Count (TLC)": {
                "ranges": {"normal_min": 4000, "normal_max": 11000, "low": 4000},
                "meaning": "White blood cells help fight infections and diseases.",
                "tips": "Maintain good hygiene, eat immune-boosting foods, and get adequate rest."
            },
            "Platelet Count": {
                "ranges": {"normal_min": 150000, "normal_max": 450000, "low": 150000},
                "meaning": "Platelets help your blood clot and prevent bleeding.",
                "tips": "Eat foods rich in folate and B12. Avoid excessive alcohol consumption."
            },
            "1 Hour ESR": {
                "ranges": {"normal_min": 0, "normal_max": 20, "low": 0},
                "meaning": "ESR indicates inflammation in your body. Higher values may suggest infection or inflammation.",
                "tips": "If elevated, follow up with your doctor. Maintain anti-inflammatory diet with turmeric and omega-3."
            },
            "HbA1c (Glycosylated Hemoglobin)": {
                "ranges": {"normal_min": 4.0, "normal_max": 6.0, "low": 4.0},
                "meaning": "HbA1c shows average blood sugar over 2-3 months. Higher values indicate diabetes risk.",
                "tips": "Control carb intake, exercise regularly, and monitor blood sugar. Consult doctor if elevated."
            },
            "Glucose, Fasting, Plasma": {
                "ranges": {"normal_min": 70, "normal_max": 100, "low": 70},
                "meaning": "Fasting glucose shows blood sugar after overnight fasting. High levels indicate diabetes.",
                "tips": "Limit sugary foods, exercise regularly, and maintain healthy weight."
            },
            "Post Prandial Glucose (PPBS)": {
                "ranges": {"normal_min": 70, "normal_max": 140, "low": 70},
                "meaning": "Post-meal glucose shows how well your body processes sugar after eating.",
                "tips": "Eat balanced meals, avoid refined sugars, and take short walks after meals."
            },
            "SGPT": {
                "ranges": {"normal_min": 10, "normal_max": 40, "low": 10},
                "meaning": "SGPT indicates liver function. Elevated levels may suggest liver damage.",
                "tips": "Limit alcohol, maintain healthy weight, and eat liver-friendly foods like garlic and green tea."
            },
            "Creatinine": {
                "ranges": {"normal_min": 0.6, "normal_max": 1.4, "low": 0.6},
                "meaning": "Creatinine indicates kidney function. High levels may suggest kidney problems.",
                "tips": "Stay well hydrated, limit protein supplements, and maintain healthy blood pressure."
            }
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
        return text
    
    def determine_test_status(self, test_name: str, value: str, unit: str, reference_range: str) -> str:
        """Determine if test result is HIGH, LOW, or NORMAL"""
        try:
            clean_value = re.sub(r'[^\d\.]', '', value)
            if not clean_value:
                return "UNKNOWN"
            
            numeric_value = float(clean_value)
            
            if test_name in self.test_reference_data:
                ranges = self.test_reference_data[test_name]["ranges"]
                if numeric_value < ranges.get("normal_min", ranges.get("low", 0)):
                    return "LOW"
                elif numeric_value > ranges.get("normal_max", 999999):
                    return "HIGH"
                else:
                    return "NORMAL"
            
            if reference_range:
                range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', reference_range)
                if range_match:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                    
                    if numeric_value < min_val:
                        return "LOW"
                    elif numeric_value > max_val:
                        return "HIGH"
                    else:
                        return "NORMAL"
            
            if value.upper() in ["POSITIVE", "PRESENT", "REACTIVE"]:
                return "ABNORMAL"
            elif value.upper() in ["NEGATIVE", "ABSENT", "NON REACTIVE", "NIL"]:
                return "NORMAL"
            
            return "NORMAL"  
            
        except (ValueError, AttributeError):
            return "UNKNOWN"
    
    def extract_basic_info(self, text: str) -> Dict[str, str]:
        info = {}
        
        patterns = {
            'registration_number': r'Reg\.\s*No\.\s*:\s*(\d+\s*\([^)]+\))',
            'patient_name': r'Name\s*:\s*([A-Z\s]+?)(?=\s+Reporting Date)',
            'age': r'Age\s*:\s*(\d+\s*Y)',
            'sex': r'Sex\s*:\s*(MALE|FEMALE)',
            'phone_number': r'Pt\.\s*Tele\s*No:\s*(\d+)',
            'collection_date': r'Collection Date\s*:\s*([\d\-]+\s+[\d:]+\s+[AP]M)',
            'reporting_date': r'Reporting Date\s*:\s*([\d\-]+\s+[\d:]+\s+[AP]M)',
            'referring_doctor': r'Ref\.\s*By\s*:\s*(DR\s+[A-Z\s]+)',
            'location': r'Location\s*:\s*([A-Z]+)',
            'pathologist': r'Pathologist\s*:\s*(Dr\.[A-Za-z\s\.]+)',
            'lab_name': r'(Airmed Pathology Pvt\.\s*Ltd\.)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info[key] = match.group(1).strip()
        
        return info
    
    def extract_hematology_tests(self, text: str) -> List[TestResult]:
        hematology_match = re.search(r'HEMATOLOGY\s*(.*?)(?=BIOCHEMISTRY|SEROLOGY|CLINICAL PATHOLOGY|\Z)', text, re.DOTALL | re.IGNORECASE)
        if not hematology_match:
            return []
            
        section_text = hematology_match.group(1)
        tests = []
        
        test_patterns = [
            (r'HEMOGLOBIN\s+([\d\.]+)\s+([a-zA-Z%]+)\s+([\d\s\-\.]+)', "HEMOGLOBIN"),
            (r'Total RBC Count\s+([\d\.]+)\s+([a-zA-Z/]+)\s+([\d\s\-\.]+)', "Total RBC Count"),
            (r'H\.CT\s+([\d\.]+)\s+([%]+)\s+([\d\s\-]+)', "H.CT"),
            (r'M\.C\.V\s+([\d\.]+)\s+([\d\s\-]+)', "M.C.V"),
            (r'M\.C\.H\.\s+([\d\.]+)\s+([a-zA-Z]+)\s+([\d\s\-]+)', "M.C.H."),
            (r'M\.C\.H\.C\.\s+([\d\.]+)\s+([%]+)\s+([\d\s\-]+)', "M.C.H.C."),
            (r'R\.D\.W\s+([\d\.]+)\s+([%]+)\s+([\d\s\-\.]+)', "R.D.W"),
            (r'Total WBC Count \(TLC\)\s+([\d]+)\s+([/a-zA-Z]+)\s+([\d\s\-]+)', "Total WBC Count (TLC)"),
            (r'Platelet Count\s+([\d]+)\s+([/a-zA-Z]+)\s+([\d\s\-]+)', "Platelet Count"),
            (r'1 Hour ESR\s+([\d]+)\s+(mm)\s+([\d\s\-]+)', "1 Hour ESR"),
            (r'Polymorphs\s+([\d]+)\s+([%]+)\s+([\d\s\-]+)', "Polymorphs"),
            (r'lymphocytes\s+([\d]+)\s+([a-zA-Z]+)\s+([\d\s\-]+)', "Lymphocytes"),
            (r'Eosinophils\s+([\d]+)\s+([%]+)\s+([\d\s\-]+)', "Eosinophils"),
            (r'Monocytes\s+([\d]+)\s+([%]+)\s+([\d\s\-]+)', "Monocytes"),
            (r'Basophils\s+([\d]+)\s+([%]+)\s+([\d\s\-]+)', "Basophils"),
            (r'PT\s+([\d\.]+)\s+(second)\s+([\d\s\-]+)', "PT (Prothrombin Time)"),
            (r'INR\s+([\d\.]+)', "INR"),
            (r'APTT\s+([\d\.]+)\s+(second)\s+([\d\s\-]+)', "APTT (Activated Partial Thrombin Time)")
        ]
        
        for pattern, test_name in test_patterns:
            match = re.search(pattern, section_text)
            if match:
                value = match.group(1)
                unit = match.group(2) if len(match.groups()) >= 2 else ""
                reference = match.group(3) if len(match.groups()) >= 3 else ""
                
                status = self.determine_test_status(test_name, value, unit, reference)
                
                tests.append(TestResult(
                    name=test_name,
                    value=value,
                    unit=unit,
                    reference_range=reference,
                    status=status
                ))
        
        abo_match = re.search(r'ABO\s+"([A-Z]+)"\s+Rh Type\s+(Positive|Negative)', section_text)
        if abo_match:
            tests.append(TestResult(
                name="ABO Blood Group",
                value=abo_match.group(1),
                status="NORMAL"
            ))
            tests.append(TestResult(
                name="Rh Type",
                value=abo_match.group(2),
                status="NORMAL"
            ))
        
        return tests
    
    def extract_biochemistry_tests(self, text: str) -> List[TestResult]:
        biochemistry_match = re.search(r'BIOCHEMISTRY\s*(.*?)(?=SEROLOGY|HEMATOLOGY|CLINICAL PATHOLOGY|\Z)', text, re.DOTALL | re.IGNORECASE)
        if not biochemistry_match:
            return []
            
        section_text = biochemistry_match.group(1)
        tests = []
        
        test_patterns = [
            (r'HBA1c \(GLYCOSYLATED\s+HEMOGLOBIN\)\s+([\d\.]+)\s+([%]+)', "HbA1c (Glycosylated Hemoglobin)"),
            (r'Mean Blood Glucose\s+([\d\.]+)\s+(mg/dL)', "Mean Blood Glucose"),
            (r'Glucose, Fasting, Plasma\s+([\d\.]+)\s+(mg/dL)\s+([\d\s\-]+)', "Glucose, Fasting, Plasma"),
            (r'POST PRANDIAL GLUCOSE \( PPBS \)\s+([\d\.]+)\s+(mg/dL)\s+([\d\s\-]+)', "Post Prandial Glucose (PPBS)"),
            (r'SGPT\s+([\d\.]+)\s+(IU/L)\s+([\d\s\-]+)', "SGPT"),
            (r'CREATININE\s+([\d\.]+)\s+(mg/dL)\s+([\d\s\-\.]+)', "Creatinine")
        ]
        
        for pattern, test_name in test_patterns:
            match = re.search(pattern, section_text)
            if match:
                value = match.group(1)
                unit = match.group(2) if len(match.groups()) >= 2 else ""
                reference = match.group(3) if len(match.groups()) >= 3 else ""
                
                status = self.determine_test_status(test_name, value, unit, reference)
                
                tests.append(TestResult(
                    name=test_name,
                    value=value,
                    unit=unit,
                    reference_range=reference,
                    status=status
                ))
        
        return tests
    
    def extract_serology_tests(self, text: str) -> List[TestResult]:
        serology_match = re.search(r'SEROLOGY/IMMUNOLOGY\s*(.*?)(?=BIOCHEMISTRY|HEMATOLOGY|CLINICAL PATHOLOGY|\Z)', text, re.DOTALL | re.IGNORECASE)
        if not serology_match:
            return []
            
        section_text = serology_match.group(1)
        tests = []
        
        hbsag_match = re.search(r'HbsAg\s+(Negative|Positive)', section_text)
        if hbsag_match:
            status = "NORMAL" if hbsag_match.group(1) == "Negative" else "ABNORMAL"
            tests.append(TestResult(
                name="HbsAg",
                value=hbsag_match.group(1),
                status=status
            ))
        
        hiv_matches = re.findall(r'HIV (I|II)\s+(Non Reactive|Reactive)', section_text)
        for match in hiv_matches:
            status = "NORMAL" if match[1] == "Non Reactive" else "ABNORMAL"
            tests.append(TestResult(
                name=f"HIV {match[0]}",
                value=match[1],
                status=status
            ))
        
        return tests
    
    def extract_clinical_pathology_tests(self, text: str) -> List[TestResult]:
        clinical_match = re.search(r'CLINICAL PATHOLOGY\s*(.*?)(?=BIOCHEMISTRY|HEMATOLOGY|SEROLOGY|\Z)', text, re.DOTALL | re.IGNORECASE)
        if not clinical_match:
            return []
            
        section_text = clinical_match.group(1)
        tests = []
        
        urine_patterns = [
            (r'Volume\s+([\d]+)\s+(ML)', "Urine Volume"),
            (r'Colour\s+(Pale Yellow|Yellow|Clear|[A-Za-z\s]+)', "Urine Colour"),
            (r'Appearance\s+(Clear|Turbid|[A-Za-z\s]+)', "Urine Appearance"),
            (r'Reaction\s+(Acidic|Alkaline|Neutral)', "Urine Reaction"),
            (r'Sp\. Gravity\s+([\d\.]+)', "Specific Gravity"),
            (r'Protein\s+(Nil|Present|Absent|\+*)', "Urine Protein"),
            (r'Glucose\s+(Present \(\+\+\)|Nil|Absent|Present|\+*)', "Urine Glucose"),
            (r'Bile Salts\s+(Absent|Present)', "Bile Salts"),
            (r'Bile Pigments\s+(Absent|Present)', "Bile Pigments"),
            (r'Pus Cells\s+([\d\-]+)', "Pus Cells"),
            (r'Red Cells\s+(NIL|\d+)', "Red Cells"),
            (r'Epithelial Cells\s+(OCCASIONAL|\d+)', "Epithelial Cells"),
            (r'Casts\s+(Absent|Present)', "Casts"),
            (r'Fungus\s+(Absent|Present)', "Fungus"),
            (r'Crystals\s+(Absent|Present)', "Crystals"),
            (r'Bacteria\s+(Absent|Present)', "Bacteria")
        ]
        
        for pattern, test_name in urine_patterns:
            match = re.search(pattern, section_text)
            if match:
                value = match.group(1)
                unit = match.group(2) if len(match.groups()) >= 2 else ""
                
                status = "NORMAL"
                if test_name in ["Urine Protein", "Urine Glucose"] and value not in ["Nil", "Absent"]:
                    status = "ABNORMAL"
                elif test_name in ["Bile Salts", "Bile Pigments", "Casts", "Fungus", "Crystals", "Bacteria"] and value == "Present":
                    status = "ABNORMAL"
                
                tests.append(TestResult(
                    name=test_name,
                    value=value,
                    unit=unit,
                    status=status
                ))
        
        return tests
    
    def create_patient_report(self, patient_text: str) -> PatientReport:
        report = PatientReport()
        
        basic_info = self.extract_basic_info(patient_text)
        for key, value in basic_info.items():
            if hasattr(report, key):
                setattr(report, key, value)
        
        report.hematology_tests = self.extract_hematology_tests(patient_text)
        report.biochemistry_tests = self.extract_biochemistry_tests(patient_text)
        report.serology_tests = self.extract_serology_tests(patient_text)
        report.clinical_pathology_tests = self.extract_clinical_pathology_tests(patient_text)
        
        abo_match = re.search(r'ABO\s+"([A-Z]+)"\s+Rh Type\s+(Positive|Negative)', patient_text)
        if abo_match:
            report.blood_group = abo_match.group(1)
            report.rh_type = abo_match.group(2)
        
        return report
    
    def analyze_pathology_report(self, pdf_path: str) -> PatientReport:
        full_text = self.extract_text_from_pdf(pdf_path)
        return self.create_patient_report(full_text)
    
    def create_json_for_generator(self, report: PatientReport) -> Dict:
        """Create JSON format expected by the PDF generator"""
        tests = []
        
        all_tests = (report.hematology_tests + report.biochemistry_tests + 
                    report.serology_tests + report.clinical_pathology_tests)
        
        for test in all_tests:
            test_data = {
                "name": test.name,
                "value": test.value,
                "unit": test.unit,
                "status": test.status
            }
            
            if test.name in self.test_reference_data:
                ref_data = self.test_reference_data[test.name]
                test_data["ranges"] = ref_data["ranges"]
                test_data["meaning"] = ref_data["meaning"]
                test_data["tips"] = ref_data["tips"]
            else:
                if test.reference_range:
                    test_data["reference_range"] = test.reference_range
                
                test_data["meaning"] = f"This test measures {test.name.lower()} levels in your body."
                test_data["tips"] = "Consult with your healthcare provider for specific recommendations based on your results."
            
            tests.append(test_data)
        
        result = {
            "patient_info": {
                "name": report.patient_name,
                "age": report.age,
                "sex": report.sex,
                "registration_number": report.registration_number,
                "collection_date": report.collection_date,
                "reporting_date": report.reporting_date,
                "lab_name": report.lab_name
            },
            "tests": tests
        }
        
        return result
    
    def save_json_for_generator(self, report: PatientReport, filename: str = "health_report_data.json"):
        """Save the report in the format expected by the PDF generator"""
        json_data = self.create_json_for_generator(report)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON file saved: {filename}")
        print(f"Total tests exported: {len(json_data['tests'])}")
        return filename

def main():
    pdf_path = r"C:\Users\adrij\OneDrive\Desktop\healthfinit\AHM-209989_result_wlpd.pdf"
    
    try:
        extractor = PathologyReportExtractor()
        print("Extracting data from PDF...")
        report = extractor.analyze_pathology_report(pdf_path)
        
        print(f"Extracted {len(report.hematology_tests)} hematology tests")
        print(f"Extracted {len(report.biochemistry_tests)} biochemistry tests")
        print(f"Extracted {len(report.serology_tests)} serology tests")
        print(f"Extracted {len(report.clinical_pathology_tests)} clinical pathology tests")
        
        json_filename = extractor.save_json_for_generator(report)
        
        print(f"\n✅ Successfully created JSON file: {json_filename}")
        print("This file can now be used by the PDF generator to create the health summary.")
        
        json_data = extractor.create_json_for_generator(report)
        if json_data["tests"]:
            print(f"\nPreview of first test:")
            print(f"Name: {json_data['tests'][0]['name']}")
            print(f"Value: {json_data['tests'][0]['value']} {json_data['tests'][0]['unit']}")
            print(f"Status: {json_data['tests'][0]['status']}")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find PDF file at {pdf_path}")
        print("Please update the pdf_path variable with the correct file location.")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()