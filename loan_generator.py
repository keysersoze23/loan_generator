import streamlit as st
from openai import OpenAI
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from io import BytesIO
import re
import base64

def generate_contract(api_key, borrower, loan_amount, interest_rate, term):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Generate a formal loan contract for Tar Heel Bank as the lender and {borrower} as the borrower.
    The loan amount is ${loan_amount}, with an interest rate of {interest_rate}% and a term of {term} months.
    Include standard legal language, terms, and conditions for a loan contract. 
    Along with the usual sections, the loan also needs to have the following sections: 
    Severability Clause, Entire Agreement Clause, Amendment Clause, Assignment, Costs and Expenses, 
    Waiver, No Waiver, Successor and Assigns, and Notices. Include a section for a Guarantee/Guarantor, 
    as well as space to fill in information about the Guarantor.
    """
    response = client.chat.completions.create(
    model="gpt-4o",  # or "gpt-3.5-turbo", depending on your access
    messages=[
        {"role": "system", "content": "You are a helpful assistant that provides legal advice in a formal tone."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=2000
    )
    
    return response.choices[0].message.content

def create_pdf(contract_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', fontSize=18, leading=22, spaceAfter=20, alignment=1))
    styles.add(ParagraphStyle(name='CustomBodyText', fontSize=12, leading=14, alignment=TA_JUSTIFY))

    def bold_asterisks(text):
        return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    flowables = []
    
    # Add title
    title = Paragraph("Loan Contract", styles['CustomTitle'])
    flowables.append(title)
    flowables.append(Spacer(1, 12))
    
    # Add contract paragraphs
    paragraphs = contract_text.split('\n\n')
    for para in paragraphs:
        formatted_para = bold_asterisks(para)
        p = Paragraph(formatted_para, styles['CustomBodyText'])
        flowables.append(p)
        flowables.append(Spacer(1, 12))
    
    doc.build(flowables)
    buffer.seek(0)
    return buffer

st.title('Tar Heel Bank Loan Contract Generator')

api_key = st.text_input('OpenAI API Key', type='password')
borrower = st.text_input('Borrower Name or Company')
loan_amount = st.number_input('Loan Amount ($)', min_value=1000, step=1000)
interest_rate = st.slider('Interest Rate (%)', 1.0, 20.0, 5.0, 0.1)
term = st.number_input('Loan Term (months)', min_value=1, max_value=360, value=12, step=1)

if st.button('Generate Contract'):
    if api_key and borrower and loan_amount and interest_rate and term:
        try:
            contract_text = generate_contract(api_key, borrower, loan_amount, interest_rate, term)
            pdf_buffer = create_pdf(contract_text)
            
            st.subheader('Generated Contract')
            st.text_area('Contract Preview', contract_text, height=300)
            
            st.download_button(
                label="Download Contract PDF",
                data=pdf_buffer,
                file_name="loan_contract.pdf",
                mime="application/pdf"
            )
            
            # Display PDF in Streamlit
            base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error('Please fill in all the required fields, including the OpenAI API key.')

