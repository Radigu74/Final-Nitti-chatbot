import os
import openai
import streamlit as st
import re
from dotenv import load_dotenv, find_dotenv
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Load environment variables
_ = load_dotenv(find_dotenv())

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize geocoder
geolocator = Nominatim(user_agent="nitti_bot")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_enabled" not in st.session_state:
    st.session_state.chat_enabled = True  # Set to True to allow input field to appear
if "chat_context" not in st.session_state:
    st.session_state.chat_context = [
        {'role': 'system', 'content': """
You are CustomerserviceBot for Nitti Safety Footwear, an automated service to assist incoming enquiries.
You first greet the customer, then assist with the enquiry regarding safety shoes,
and then ask if our sales can reach out to them.
If you do not know the answer, ask if it is okay that Mr. Harmsen contacts them.
You wait to collect all the information, then summarize it and check for a final time if the customer needs anything else.
Finally, request their phone number and email.
When asking for a phone number, always check the country code.
Ensure clarity on product models, accessories, and customer details.
You respond in a short, friendly, and conversational style, without repeating questions more than twice.
Orders cannot be placed via this chatbot; instead, collect the user's contact details for a sales follow-up.

The list includes:
Low cut models:
- 21281, black, Rating: CE EN 20345:2011 S1P SRC, Model: Lace, Size: 2-14 (UK) / 35-48 (EU), Upper: Leather, Lining: Genuine Cambrelle®, 
  Outsole: Direct Injection Polyurethane
- 21381, Rating: CE EN 20345:2011 S1P SRC, Type: Low Cut, Model: Velcro & Ventilated, Size: 2-14 (UK) or 35-48 (EU), Color: Black or Brown, Upper: Leather,
  Lining: Cambrelle®, Outsole: Direct Injection Polyurethane
- 21981 black, Rating: CE EN 20345:2011 S1P SRC, Type: Low Cut, Model: Slip-on, Size: 2-14 (UK) or 35-48 (EU), Color: Black, Upper: Leather, Lining: Cambrelle®, Outsole: Direct Injection Polyurethane

High cut models:
- 23281 black and brown, CE EN 20345:2011 S3 SRC, Type: High Cut, Model: Pull-on, Size: 2-14 (UK) or 35-48 (EU), Upper: Water Resistant Leather, Lining: Cambrelle®, Outsole: Direct Injection Polyurethane
- 23681 black and brown, CE EN 20345:2011 S3 SRC, Type: High Cut, Model: zipper, Size: 2-14 (UK) or 35-48 (EU), Upper: Water Resistant Leather, Lining: Cambrelle®, Outsole: Direct Injection Polyurethane
- 23381 black and brown, CE EN 20345:2011 S3 SRC, Type: High Cut, Model: lace, Size: 2-14 (UK) or 35-48 (EU), Upper: Water Resistant Leather, Lining: Cambrelle®, Outsole: Direct Injection Polyurethane

Accessories:
- Socks
- Shoe Guard
- T-shirt
- Mouse pad

Information about the models you use during the conversation:
- Models to be used in wet and waterproof environments are the mid and high cut models, not the low cut.
- 21281: This model is designed to provide you with extra comfort during those long working hours.
- 21981: A general purpose and well ventilated model with an industrial grade Velcro strap for added functionality.
  Improved ventilation to maintain comfort for workers in hot environments.


Safety ratings:
- Indonesia Rating: SNI 7079-2009
- Singapore Rating: SS 513
- China Rating: GB 21148
- Malaysia Rating: Sirim
- Other: As/NZS 2210.3.2019 and OSHC

Information about direct injection to use:
Direct injection is the process where the PU is directly injected into the mold as opposed to glued to the upper of the shoe. 
This ensures a better bond and is of higher quality than non-direct injection.

Warranty information:
Nitti Safety Footwear is warranted for six (6) months from the date of invoice by Nitti to its distributors
against defects in materials and/or workmanship when used under normal conditions for its intended purpose.

Return policy:
As a requirement of the warranty mentioned above, the purchaser must return the footwear to Nitti for assessment together with proof of purchase or receipt.
Following assessment, if Nitti determines that the footwear is defective as the result of normal use, Nitti will replace the footwear.

Boot care:
1. Do not store your boots in direct sunlight. Always air-dry your boots after use and store them in a cool, dry, and well-ventilated place.
2. Clean and polish your boots regularly with wax to enhance durability. Be sure to rinse your boots with water after contact with cement. 
   Left unattended, cement will damage the leather upper, drying it out and causing cracks to form.
3. Do not wash your boots. Wet boots should be air-dried naturally at room temperature with the cushion footbed and laces removed and the boots fully opened. 
   Never force dry or use strong detergents or caustic cleaning agents.
"""} ]

# ✅ Validation functions
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return re.match(r"^\+?\d{10,15}$", phone)

def validate_postal(postal_code):
    return re.match(r'^\d{6}$', postal_code) is not None

def get_coordinates(postal_code):
    try:
        location = geolocator.geocode(postal_code + ", Singapore")
        return (location.latitude, location.longitude) if location else None
    except Exception as e:
        st.error(f"Error fetching coordinates: {e}")
        return None

def find_nearest_store(postal_code):
    if not validate_postal(postal_code):
        return "Invalid postal code format."

    user_coords = get_coordinates(postal_code)
    if not user_coords:
        return "Could not find location."

    nearest_store = min(
        stores.items(),
        key=lambda store: geodesic(user_coords, store[1]["coordinates"]).kilometers
    )

    store_name, store_data = nearest_store
    return f"Nearest store: {store_name} ({store_data['address']}, Tel: {store_data['tel']}, Distance: {geodesic(user_coords, store_data['coordinates']).kilometers:.2f} km)"


# ✅ Predefined store locations
stores = {
    "H K ENGINEERING PTE LTD - 49 Joo Koon Cir": {
        "coordinates": (1.3273, 103.6730),
        "address": "49 Joo Koon Cir, Singapore 629068",
        "tel": "6565 5555"
    },
    "KOON HIN LEE SAFETY PRODUCTS - 221 Boon Lay Place, Boon Lay Shopping Centre": {
        "coordinates": (1.3474, 103.7138),
        "address": "221 Boon Lay Place #01-238, Boon Lay Shopping Centre, 640221",
        "tel": "6268 0401"
    },
    "TAKA HARDWARE & ENGINEERING PTE LTD - 32 Lok Yang Way": {
        "coordinates": (1.3216, 103.6851),
        "address": "32 Lok Yang Way, Singapore 628639",
        "tel": "6842 0782"
    },
    "SINYOU HARDWARE PTE LTD - 5 Soon Lee St, Pioneer Point": {
        "coordinates": (1.3275, 103.6961),
        "address": "5 Soon Lee St #01-21, Pioneer Point, Singapore 627607",
        "tel": "6710 5955"
    },
    "MUI HUAT TRADING - 221 Boon Lay Place, Boon Lay Shopping Centre": {
        "coordinates": (1.3474, 103.7138),
        "address": "221 Boon Lay Place #01-238, Boon Lay Shopping Centre, Singapore 640221",
        "tel": "6261 3590"
    },
    "NS HARDWARE PTE LTD - 2 Buroh Cres, Ace@Buroh": {
        "coordinates": (1.3262, 103.6987),
        "address": "2 Buroh Cres, #01-15, Ace@Buroh, Singapore 627546",
        "tel": "6029 3113"
    },
    "AGGREGATES ENGINEERING PTE LTD - 2B Tuas Ave 12": {
        "coordinates": (1.3221, 103.6525),
        "address": "2B Tuas Ave 12, Singapore 639048",
        "tel": "6741 4638"
    },
    "SIN HILL INTERNATIONAL PTE LTD - 11 Woodlands Close": {
        "coordinates": (1.4289, 103.7954),
        "address": "11 Woodlands Close #05-32, Singapore 737853",
        "tel": "6555 1658"
    },
    "ISSA LEATHER BAGS AND SHOES SHOP - 4 Woodlands Street 12, Marsiling Mall": {
        "coordinates": (1.4337, 103.7741),
        "address": "4 Woodlands Street 12, #02-49, Marsiling Mall, Singapore 738623",
        "tel": "6269 5178"
    },
    "KIAN HUAT ENTERPRISES - 39 Woodlands Cl, Mega@Woodlands": {
        "coordinates": (1.4305, 103.7852),
        "address": "39 Woodlands Cl, #01-13, Mega@Woodlands, Singapore 737856",
        "tel": "6779 9686"
    },
    "UNIQUE HARDWARE PTE LTD - 30 Kranji Loop, TimMac@Kranji": {
        "coordinates": (1.4267, 103.7623),
        "address": "30 Kranji Loop BlkB, #04-17, TimMac@Kranji, 739570",
        "tel": "6748 4211"
    },
    "JAHO TRADING PTE LTD - 60 Jalan Lam Huat, Carros Centre": {
        "coordinates": (1.4316, 103.7859),
        "address": "60 Jalan Lam Huat #01-16, Carros Centre, Singapore 737869",
        "tel": "6481 7305"
    },
    "KIANG SING HONG PTE LTD - 280 Woodlands Industrial Park E5, Harvest Building": {
        "coordinates": (1.4472, 103.7920),
        "address": "280 Woodlands Industrial Park E5 #01-45/46, Harvest Building, Singapore 757322",
        "tel": "6760 0365"
    },
    "KIAW AIK HARDWARE TRADING PTE LTD - 321 Jln Besar": {
        "coordinates": (1.3098, 103.8571),
        "address": "321 Jln Besar, Singapore 208979",
        "tel": "6296 8858"
    },
    "MQ HARDWARE & ELECTRICAL TRADING PTE LTD - 3 Toa Payoh Industrial Park": {
        "coordinates": (1.3323, 103.8518),
        "address": "3 Toa Payoh Industrial Park, #01-1361, Singapore 319055",
        "tel": "9665 2756"
    },
    "NIRJA MINI MART PTE.LTD - 66 Desker Road": {
        "coordinates": (1.3077, 103.8559),
        "address": "66 Desker Road, Singapore 209589",
        "tel": "8182 3815"
    },
    "HAN SIANG HARDWARE PTE LTD - 30 Kelantan Rd": {
        "coordinates": (1.3056, 103.8583),
        "address": "30 Kelantan Rd, #01-83, Singapore 200030",
        "tel": "6294 5395"
    },
    "TROSEAL BUILDING MATERIALS PTE LTD - 637 Veerasamy Rd": {
        "coordinates": (1.3065, 103.8568),
        "address": "637 Veerasamy Rd, #01-123/125, Singapore 200637",
        "tel": "6298 1123"
    },
    "YIAP HENG CHEONG HARDWARE PTE LTD - 294 Balestier Rd": {
        "coordinates": (1.3204, 103.8525),
        "address": "294 Balestier Rd, Singapore 329973",
        "tel": "6254 4623"
    },
    "FRANCE SHOES COMPANY PTE LTD - 1 Park Road, People’s Park Complex": {
        "coordinates": (1.2852, 103.8442),
        "address": "1 Park Road, #02-35, People’s Park Complex, Singapore 059108",
        "tel": "6535 0042"
    },
    "TECK MENG HARDWARE PTE LTD - 5030 Ang Mo Kio Ind Park 2": {
        "coordinates": (1.3687, 103.8602),
        "address": "5030 Ang Mo Kio Ind Park 2, #01-221, Singapore 569533",
        "tel": "9763 5706"
    },
    "FASTENER GROUP PTE LTD - 8 Kaki Bukit Ave 4, Premier @Kaki Bukit": {
        "coordinates": (1.3367, 103.9067),
        "address": "8 Kaki Bukit Ave 4, #03-20, Premier @Kaki Bukit, Singapore 415875",
        "tel": "6384 6355"
    },
    "LEONG SENG INDUSTRIAL PTE LTD - 5070 Ang Mo Kio Ind Park 2": {
        "coordinates": (1.3693, 103.8591),
        "address": "5070 Ang Mo Kio Ind Park 2, #01-1491, Singapore 569567",
        "tel": "6483 2409"
    },
    "CHANG TAI CHIANG HARDWARE PTE LTD - 5071 Ang Mo Kio Ind Park 2": {
        "coordinates": (1.4013, 103.8158),
        "address": "5071 Ang Mo Kio Ind Park 2, Singapore 787812",
        "tel": "6481 0231"
    },
    "NAM YONG INDUSTRADES - 10 Kaki Bukit Rd 2, First East Centre": {
        "coordinates": (1.3359, 103.9058),
        "address": "10 Kaki Bukit Rd 2, #01-02, First East Centre, Singapore 417868",
        "tel": "6382 5465"
    },
    "HORME HARDWARE - 1 Ubi Crescent, Number One Building": {
        "coordinates": (1.3299, 103.8944),
        "address": "1 Ubi Crescent #01-01, Number One Building, Singapore 408563",
        "tel": "6840 8855"
    },
    "HORME HARDWARE - 341 Changi Road": {
        "coordinates": (1.3223, 103.9063),
        "address": "341 Changi Road, Singapore 419812",
        "tel": "6840 8844"
    },
    "MENG TAT HARDWARE CO - 6 Ubi Road 1, Wintech Centre": {
        "coordinates": (1.3270, 103.8980),
        "address": "6 Ubi Road 1 #01-08/09, Wintech Centre, Singapore 408726",
        "tel": "6292 9484"
    },
    "CHIN HOE HUP KEE HARDWARE - 139 Tampines St 11": {
        "coordinates": (1.3457, 103.9443),
        "address": "139 Tampines St 11, #01-26, Singapore 521139",
        "tel": "6785 1910"
    },
    "LI FONG HARDWARE ENTERPRISE - 3018 Bedok North Street 5, EastLink": {
        "coordinates": (1.3341, 103.9531),
        "address": "3018 Bedok North Street 5, #01-18, EastLink, Singapore 486132",
        "tel": "6444 6231"
    },
    "B&S (2017) HARDWARE PTE LTD - 308 Geylang Road": {
        "coordinates": (1.3137, 103.8804),
        "address": "308 Geylang Road, Singapore 389348",
        "tel": "9616 6571"
    },
    "J&E TRADING PTE LTD - 117 Upper East Coast Road": {
        "coordinates": (1.3125, 103.9228),
        "address": "117 Upper East Coast Road, #01-01, Singapore 455243",
        "tel": "8918 0458"
    },
    "AGGREGATES ENGINEERING PTE LTD - 3024 Ubi Road 3, Kampong Ubi Industrial Estate": {
        "coordinates": (1.3302, 103.8981),
        "address": "3024 Ubi Road 3, #02-71, Kampong Ubi Industrial Estate, Singapore 408652",
        "tel": "6741 4638 / 69 / 72"
    }
}

# ✅ Inject Store Locations into Chat Context
if "store_context" not in st.session_state:
    store_info = "\n".join(
        f"{name}: 📍 {info['address']}, 📞 {info['tel']}"
        for name, info in stores.items()
    )
    st.session_state.store_context = [
        {"role": "system", "content": f"The available store locations are:\n{store_info}"}
    ]

# ✅ Ensure chatbot context includes store details
if "chat_context" not in st.session_state:
    st.session_state.chat_context = [
        {'role': 'system', 'content': "You are CustomerserviceBot for Nitti Safety Footwear. You assist with store locations and safety footwear inquiries."}
    ] + st.session_state.store_context

    
# ✅ OpenAI communication function
def get_completion_from_messages(user_messages, model="gpt-3.5-turbo", temperature=0):
    client = openai.OpenAI()

    messages = st.session_state.chat_context + user_messages

    # ✅ Ensure chatbot prioritizes store locations when asked
    if any(kw in user_messages[-1]["content"].lower() for kw in ["store", "nearest", "location", "buy", "address"]):
        store_info = "\n".join(
            f"{name}: 📍 {info['address']}, 📞 {info['tel']}"
            for name, info in stores.items()
        )
        messages.append({"role": "system", "content": f"Here are the store locations:\n{store_info}"})

    response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    
    return response.choices[0].message.content  # ✅ Now correctly inside the function




# ✅ User Details Input
st.title("Nitti Safety Footwear Chatbot")
st.markdown("📢 **Enter your contact details before chatting:**")

email = st.text_input("Enter your email:", key="email_input")
phone = st.text_input("Enter your phone number:", key="phone_input")
country = st.selectbox("Select Country", ["Singapore", "Malaysia", "Indonesia"], key="country_dropdown")
postal = st.text_input("Enter your postal code (Required if in SG):", key="postal_input")

# ✅ Validation function
def validate_and_start():
    if not is_valid_email(email):
        return "❌ Invalid email."
    if not is_valid_phone(phone):
        return "❌ Invalid phone number."
    if country == "Singapore" and not validate_postal(postal):
        return "❌ Invalid postal code."

    st.session_state.chat_enabled = True

 # ✅ Validation function
def validate_and_start():
    if not is_valid_email(email):
        return "❌ Invalid email."
    if not is_valid_phone(phone):
        return "❌ Invalid phone number."
    if country == "Singapore" and not validate_postal(postal):
        return "❌ Invalid postal code."

    st.session_state.chat_enabled = True

    # ✅ Call `find_nearest_store()` and inject result into chatbot context
    if country == "Singapore":
        store_info = find_nearest_store(postal)
        st.session_state.chat_context.append(
            {"role": "system", "content": f"The nearest store to the user is: {store_info}"}
        )
    else:
        store_info = "No store information available for this country."

    return f"✅ **Details saved! {store_info}**"  # ✅ Now correctly inside a function


# ✅ Run validation on button click
if st.button("Submit Details", key="submit_button"):
    validation_message = validate_and_start()
    st.markdown(validation_message, unsafe_allow_html=True)


# ✅ Display Chat History
st.markdown("---")
st.markdown("**💬 Chat with the Nitti Safety Footwear Bot:**")

for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**User:** {chat['content']}")
    else:
        st.markdown(f"<div style='background-color: #F6F6F6; padding: 10px; border-radius: 5px;'>"
                    f"**Nitti CS:** {chat['content']}</div>",
                    unsafe_allow_html=True)

# ✅ Ensure `chat_input_key` is initialized
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0

# ✅ Display chat input field (new key forces refresh)
if st.session_state.chat_enabled:
    user_input = st.text_input(
        "Type your message and press Enter:",
        key=f"chat_input_{st.session_state.chat_input_key}",
        value=""
    )

   # ✅ Ensure Send button works correctly
    if st.button("Send", key="send_button"):
        if user_input.strip():  # Only process non-empty input
            # ✅ Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

            # ✅ Get chatbot response (Ensure context is included)
            response = get_completion_from_messages(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

            # ✅ Instead of modifying `st.session_state["chat_input"]`, increment key to refresh input field
            st.session_state.chat_input_key += 1  

            # ✅ Force UI update to refresh the input field
            st.rerun()
