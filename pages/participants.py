import streamlit as st
import utils.streamlit_utils as st_utils
import utils.constants as constants

st_utils.create_page_setup(page_name="Participant Information")


# Read the PDF file as binary
with open(f"{constants.PATH_PDFS}/Participant_Information_Sheet.pdf", "rb") as pdf_file:
    pdf_pis = pdf_file.read()

with open(f"{constants.PATH_PDFS}/Participant_Agreement_Form.pdf", "rb") as pdf_file:
    pdf_paf = pdf_file.read()



st.write("Download a copy of each form:")
download_cols = st.columns([1, 1, 0.65])

with download_cols[0]:
    st.download_button(
        label="Participant Information Sheet",
        data=pdf_pis,
        file_name="Participant_Information_Sheet.pdf",
        mime="application/pdf",
        icon=":material/download:",
    )

with download_cols[1]:
    st.download_button(
        label="Participant Agreement Form",
        data=pdf_paf,
        file_name="Participant_Agreement_Form.pdf",
        mime="application/pdf",
        icon=":material/download:",
    )

tab_pis, tab_paf = st.tabs(["Participant Information Sheet", "Participant Agreement Form"])


with tab_pis:

    left_co, cent_co,last_co = st.columns([1, 3, 1])
    with cent_co:
        st.image(f"{constants.PATH_IMAGES}/BU-CivicSage-Logo.png")

    # Header
    st.write("# Participant Information Sheet")

    # Sub-header for reference
    st.write("**Ref & Version:** Version 1\n**Ethics ID:** 61911")

    # Research Project Title
    st.write("### Research Project Title:")
    st.write("""
    - **What does my MP think? Enhancing access to localised political information via a multi-method approach**  
    - Otherwise identified as 'Civic Sage' (artefact name)
    """)

    # Section 1: Purpose of the Research
    st.write("### What is the purpose of the research/questionnaire?")
    st.write("""
    - This research is being completed, in partial requirement of a student Bachelor’s Degree dissertation project for Bournemouth University, Faculty of Science and Technology. This project aims to develop an **AI and data-analytics driven web-service** that anyone can use to query information about their local Member of Parliament (MP).
    
    - Participants will be asked to spend 15 minutes using this service. Data is then collected (via the survey) to understand **participants' engagement** with the service: where they find it useful, pain points, general comments, and so forth. Participants will take part in a survey based on their technical expertise.
    """)

    # Section 2: Why have I been chosen?
    st.write("### Why have I been chosen?")
    st.write("""
    - Participants for this project have been chosen based on two groups:
    1. **Non-technical users** who are interested in understanding how they use the project artefact or 'service'.
    2. **Technical users** (or 'professionals') who are interested in understanding professional insight into the technical design aspects of the service.
    
    - Your participation will be modelled **dependent** on which group you belong to. This will be clearly labelled to you **prior to participation**, and at first when **originally approached** to participate in this study.
    """)

    # Section 3: Do I have to take part?
    st.write("### Do I have to take part?")
    st.write("""
    It is up to you to decide whether or not to take part – it is **not mandatory** in any way. You can withdraw from participation at any time and without giving a reason, by exiting the survey webpage.

    Please note that once you have completed and submitted your survey responses, we are **unable to remove** your anonymised responses from the study. Deciding to take part or not will not impact upon you in any way.
    """)

    # Section 4: Duration of Survey
    st.write("### How long will the questionnaire/online survey take to complete?")
    st.write("It should take no more than **5-10 minutes** to complete the survey.")

    # Section: Advantages and Possible Disadvantages
    st.write("### What are the advantages and possible disadvantages or risks of taking part?")
    st.write("""
    - Whilst there are no immediate benefits for those people participating in the project, it is hoped that this work will enhance understanding of public engagement with political **communication**, and their general preferences for political engagement.
    """)

    # Section: Type of Information Collected
    st.write("### What type of information will be sought from me and why is **the collection of** this information relevant for achieving the research project's objectives?")
    st.write("""
    - You will be asked questions relating to your experience using the service. This will help us to understand user feedback and more accurately gauge the relevant political use cases of the service to a general audience.
    """)

    # Section: Use of Information
    st.write("### Use of my information")
    st.write("""
    - Participation in this study is on the basis of **consent**: you do not have to complete the survey, and you can change your mind at any point before submitting the survey responses. We will use your data **on the basis** that it is necessary for the conduct of research, which is an activity in the public interest. We put safeguards in place to ensure that your responses are kept secure and only used as necessary for this research study and associated activities such as a research audit. Once you have submitted your survey response it will not be possible for us to remove it from the study analysis because you will not be identifiable.

    - The anonymous information collected may be used to support other ethically reviewed research projects in the future and access to it in this form will not be restricted. It will not be possible for you to be identified from this data.
    """)

    # Section: Contact for Further Information
    st.write("### Contact for further information")
    st.write("""
    If you have any questions or would like further information, please contact:
    - **James Vine** at s5311105@bournemouth.ac.uk (student, project author) or;
    - **Dr. Vegard Engen** at vengen@bournemouth.ac.uk (academic, project supervisor)
    """)

    # Section: Complaints
    st.write("### In case of complaints")
    st.write("""
    - Any concerns about the study should be directed to Professor Tiantian Zhang, Deputy Dean for Research & Professional Practice, Faculty of Science & Technology, Bournemouth University by email to researchgovernance@bournemouth.ac.uk.
    """)



with tab_paf:
    left_co, cent_co,last_co = st.columns([1, 3, 1])
    with cent_co:
        st.image(f"{constants.PATH_IMAGES}/BU-CivicSage-Logo.png")

    # Title
    st.write("# Participant Agreement Form")

    # Ref and Ethics Information
    st.write("**Ref & Version:** Version 1\n**Ethics ID:** 61911")

    # Full Title of the Project
    st.write("### Full title of project (\"the Project\"):")
    st.write("""
    - **What does my MP think? Enhancing access to localised political information via a multi-method approach**  
    - Otherwise identified as 'Civic Sage' (artefact name)
    """)

    # Researcher Details
    st.write("### Name, position and contact details of researcher:")
    st.write("""
    - **James Vine**, BSc Data Science and Analytics Student, **s5311105@bournemouth.ac.uk**
    """)

    # Supervisor Details
    st.write("### Name, position and contact details of supervisor:")
    st.write("""
    - **Dr. Vegard Engen**, Associate Professor, **vengen@bournemouth.ac.uk**
    """)

    # Section A: Agreement
    st.write("## Section A: Agreement to participate in the study")
    st.write("""
    You should only agree to participate in the study if you agree with all of the statements in this table and accept that participating will involve the listed activities.
    """)

    # Agreement Statements
    st.write("""
    - I have read and understood the Participant Information Sheet (Version 1) and have been given access to the **BU Research Participant Privacy Notice**, which sets out how we collect and use personal information ([https://www1.bournemouth.ac.uk/about/governance/access-information/data-protection-privacy](https://www1.bournemouth.ac.uk/about/governance/access-information/data-protection-privacy)).

    - I have had an opportunity to ask questions (to James Vine, **s5311105@bournemouth.ac.uk**).

    - I understand that my participation is voluntary. I can stop participating in research activities at any time without giving a reason and I am free to decline to answer any particular question(s).

    - I understand that taking part in the research will include the following activity/activities as part of the research:
        - **Using/testing the 'service'** for approximately 10-15 minutes.  
        _Please note that 'conversations' with the interface are anonymously logged, and all personal identifying information is discarded._
        - **Answering pre-determined questions** from the provided questionnaire for approximately 10-15 minutes.
        - **My words** may be quoted in publications, reports, web pages, and other research outputs without using my real name.

    - I understand that, if I withdraw from the study, I will also be able to withdraw my data from further use in the study **except** where my data has been anonymised (as I cannot be identified), or it will be harmful to the project to have my data removed.

    - I understand that my data may be used in an anonymised form by the research team to support other ethically approved research projects in the future, including future publications, reports or presentations.
            
    """)
