"""
Test script to validate template processing with Apollo dataset sample.
"""

import json
from src.models.schemas import ApifyProspect

# Load a sample record from the Apollo dataset
def test_template_conversion():
    """Test the template conversion with real Apollo data."""
    
    # Sample Apollo data (first record from the dataset)
    sample_apollo_data = {
        "first_name": "Marius",
        "last_name": "Baumgart",
        "email": "marius.baumgart@brueggemann.com",
        "organization_name": "Brüggemann",
        "organization_website_url": "http://www.brueggemann.com",
        "linkedin_url": "http://www.linkedin.com/in/marius-baumgart-a79608137",
        "name": "Marius Baumgart",
        "photo_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2",
        "title": "Head of IT | Leiter IT",
        "industry": "chemicals",
        "headline": "IT-Leiter | Digitalisierung | Cloud & Security | IT-Strategie & Transformation",
        "seniority": "head",
        "estimated_num_employees": "80",
        "city": "Heilbronn",
        "state": "Baden-Wuerttemberg",
        "country": "Germany",
        "organization_logo_url": "https://zenprospect-production.s3.amazonaws.com/uploads/pictures/68bbef3aa7abc700017744dc/picture",
        "organization_annual_revenue": "85400000",
        "organization_annual_revenue_printed": "85.4M",
        "organization_seo_description": "Startseite ▷ wir liefern welt­weit maßge­schnei­derte Lösungen  ✔ Kunst­stof­f­ad­di­tive, Indus­trie­che­mi­ka­lien und Alkohol ✔ seit 1868 ✔ jetzt klicken!",
        "organization_short_description": "Since 1868 Brüggemann has been finding and delivering custom-tailored and pioneering solutions for our customers in the field of polymer additives, industrial chemicals, and alcohol.",
        "organization_total_funding": None,
        "organization_total_funding_printed": None,
        "keywords": "chemistry, polymer additives, industrial chemicals, alcohol, chemical manufacturing, custom solutions, plastic additives, reducing agents, zinc derivatives, toll production, formaldehyde-free agents",
        "organization_technologies": "DoubleClick, DoubleClick Conversion, Google Analytics, Google Dynamic Remarketing, Google Tag Manager, Mobile Friendly, Nginx, Outlook, Sophos, reCAPTCHA",
        "email_domain_catchall": True,
        "id": "5c3d4b4cf651254691207a88",
        "organization_id": "5fca0307b1b34300013a5203",
        "twitter_url": None,
        "facebook_url": None,
        "organization_linkedin_url": "http://www.linkedin.com/company/brueggemann",
        "organization_linkedin_uid": "69799293",
        "organization_twitter_url": None,
        "organization_facebook_url": None,
        "organization_founded_year": 1868,
        "organization_primary_domain": "brueggemann.com",
        "organization_phone": "+49 7131 15750",
        "organization_street_address": "131 Salzstrasse",
        "organization_raw_address": "Salzstraße 131, Heilbronn, Baden-Wuerttemberg 74076, DE",
        "organization_state": "Baden-Wuerttemberg",
        "organization_city": "Heilbronn",
        "organization_country": "Germany",
        "organization_postal_code": "74076",
        "organization_market_cap": None,
        "raw_data": {}  # Will be populated
    }
    
    try:
        print("🧪 Testing ApifyProspect template conversion...")
        
        # Add raw data for template generation
        sample_apollo_data["raw_data"] = sample_apollo_data.copy()
        
        # Test schema validation
        prospect = ApifyProspect(**sample_apollo_data)
        print("✅ Schema validation successful!")
        
        # Test template conversion
        template_row = prospect.to_template_row()
        
        print("\n📋 Template Row Output:")
        print("=" * 60)
        for key, value in template_row.items():
            print(f"{key:20}: {str(value)[:80]}{'...' if len(str(value)) > 80 else ''}")
        
        print("\n✅ Template conversion successful!")
        print(f"📊 Generated {len(template_row)} template fields")
        
        # Verify all template fields are present
        expected_fields = [
            "Full Name", "Last Name", "First Name", "Email", "Title", 
            "Personal LinkedIn", "Company Name", "Company Website", 
            "Company LinkedIn", "Personal Summary", "Company Background", 
            "Recent Company News", "Key Offerings", "Customer Sentiment", 
            "Company Summary", "Outreach Message"
        ]
        
        missing_fields = [field for field in expected_fields if field not in template_row]
        if missing_fields:
            print(f"⚠️ Missing template fields: {missing_fields}")
        else:
            print("✅ All template fields present!")
        
        print("\n🎉 Template processing test completed successfully!")
        
    except Exception as e:
        print(f"❌ Template processing test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_template_conversion()
