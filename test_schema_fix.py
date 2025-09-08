"""
Test script to validate the updated ApifyProspect schema with actual Apollo data.
"""

from src.models.schemas import ApifyProspect
import json

# Sample Apollo data from the error output
sample_apollo_data = {
    "first_name": "Pawan",
    "last_name": "Patekar", 
    "email": "j.hohmeier@dungs.com",
    "organization_name": "DUNGS Combustion Controls",
    "organization_website_url": "http://www.dungs.com",
    "linkedin_url": "http://www.linkedin.com/in/jan-hohmeier-5624a11a1",
    "name": "Pawan Patekar",
    "photo_url": "https://media.licdn.com/dms/image/v2/C4D03AQFbweZ3tUAYPA/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1632992276870?e=2147483647&v=beta&t=Zq7Iwhn7sN6--nmXg6Cw1cVlcve1VpDW7AP6G8IuiJY",
    "title": "Head of IT",
    "industry": "machinery",
    "headline": "Team Leader - Operations @InfuseB2B | Demand Generation",
    "seniority": "head",
    "estimated_num_employees": "160",
    "city": "Urbach",
    "state": "Baden-Wuerttemberg", 
    "country": "Germany",
    "organization_logo_url": "https://zenprospect-production.s3.amazonaws.com/uploads/pictures/68bab4fad14a650001377517/picture",
    "organization_annual_revenue": "26614000",
    "organization_annual_revenue_printed": "26.6M",
    "organization_seo_description": "Safe and secure for the futureDUNGS is a synonym for safe and clean gas combustion. We develop and manufacture innovative system solutions for the thermal...",
    "organization_short_description": "Welcome to DUNGS! Over 600 associates across the globe are designing, manufacturing and marketing DUNGS products for gas safety and control technology.",
    "organization_total_funding": None,
    "organization_total_funding_printed": None,
    "keywords": "machinery manufacturing, combustion controls, gas safety, heating solutions, process heat, gas engines",
    "organization_technologies": "Microsoft Office 365, Mobile Friendly, Nginx, Outlook, Zopim",
    "email_domain_catchall": False,
    "id": "6092a5ea58b98f0001163f31",
    "organization_id": "5b84173ef874f724a6854c06",
    "twitter_url": None,
    "facebook_url": None
}

def test_schema_validation():
    """Test the updated schema with Apollo data."""
    try:
        print("🧪 Testing ApifyProspect schema with Apollo data...")
        
        # Test validation
        prospect = ApifyProspect(**sample_apollo_data)
        print("✅ Schema validation successful!")
        
        # Test computed properties
        print(f"📋 Company Name: {prospect.company_name}")
        print(f"🌐 Company Domain: {prospect.company_domain}")
        print(f"🏭 Company Industry: {prospect.company_industry}")
        print(f"👥 Company Size: {prospect.company_size}")
        print(f"📍 Location: {prospect.location}")
        print(f"💼 Effective Title: {prospect.effective_title}")
        
        # Test conversion methods
        prospect_row = prospect.to_prospect_row()
        company_row = prospect.to_company_row()
        
        print("\n📊 Prospect Row:")
        for key, value in prospect_row.items():
            print(f"  {key}: {value}")
            
        print("\n🏢 Company Row:")
        for key, value in company_row.items():
            print(f"  {key}: {value}")
            
        print("\n🎉 All tests passed! Schema is ready for production.")
        
    except Exception as e:
        print(f"❌ Schema validation failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_schema_validation()
