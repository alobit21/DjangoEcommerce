from django.shortcuts import render, get_object_or_404
from .models import Product

def product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product/product.html', {'product': product})

THE UNIVERSITY OF DODOMA
COLLAGE OF INFORMATICS AND VIRTUAL EDUCATION
 
INDUSTRIAL TRAINING REPORT IN TANZANIA
Department: Computer Science and Engineering
Company Name: CODEBLOCK Company Limited
Field Location: Mbezi beach,Kinondoni, Dar es salaam
Student Name: Aloyce Charles Mtavangu
RegNo: T22-03-06093
Degree Program: Bcs.SE
Submitted to: Mr. Mrutu.
Year: 2024/2025

       




i
CONTENTS
Cover-page ………………………………………………………………………….…………………………………...I
Contents……………………………………………………………………………………………………………………ii
LIST OF FIGURES	2
Acknowledgement	3
CHAPTER ONE	5
1.1 Overview of the Organization	5
1.2 Objectives of the Field Experience	6
1.2.1 Understanding Software Development Practices.	6
1.2.2 Learning React and Next.js Frameworks.	6
1.2.4 Enhancing Collaboration and Teamwork Skills.	7
1.2.6 Exploring the Full Development Cycle.	7
CHAPTER TWO	8
2.1 Overview of Technologies	8
2.1.1 Introduction to React	8
2.1.2 Benefits of Using React	9
2.1.3 Hands-On Projects	10
2.1.4  Routing with Next.js:	15
2.1.5 State Management:	16
2.1.6 Styling and Responsiveness:	16
CHAPTER THREE	17
3.1 Challenges Faced	17
3.2 Understanding Component Lifecycle	17
3.3 State Management Complexities	18
3.4 Asynchronous Data Fetching.	18
3.5 Navigating Git and Version Control	20
CHAPTER FOUR	20
4.1 Observations on Work Environment	20
4.1.1 Organizational Culture	20
4.1.2 Tools and Technologies Used	22
CHAPTER FIVE	23
5.1 Skills Developed	23
5.1.1 Technical Skills	23
5.2.1 Soft Skills	24
CHAPTER SIX	25
6.1  Conclusion and Recommendations.	25
6.1.1 Conclusion	25
6.1.2 Recommendations.	25
CHAPTER SEVEN	26
7.0 References	26
7.1 Books:	26
7.2 Online Tutorials:	26
7.3 Courses:	27
7.4 Blogs and Articles:	27


                                                                 ii 

LIST OF FIGURES.
Figure 1: Navigation Bar view on Desktop…………………………………………………………..10

Figure 2: Navigation Bar Component on Mobile………………………………………………….10

Figure 3: Hero Section view on Desktop………………………………………………………………10

Figure 4: Hero Section view on Mobile…………………………………………………………………11

Figure 5: About Section view on Desktop…………………………………………………………….11

Figure6:  About Section view on Mobile……………………………………………………………….12

Figure 7: Projects Section view on Desktop…………………………………………………………..12

Figure8: Projects Section view on Mobile……………………………………………………………..13

Figure 9: Contact Section view on Desktop…………………………………………………………..13

Figure10: Contact Section view on Mobile……………………………………………………………14

Figure 11: About Section view on Desktop……………………………………………………………14

Figure12: About Section view on Mobile……………………………………………………………….15


                                                                  iii


Acknowledgement
I would like to sincerely thank CODEBLOCK and the entire team for their support and guidance during my industrial training. Their mentor-ship and supervision were essential in helping me reach my goals and gain hands-on experience in the field.
A special thank you to Engineer Mbunji for his continuous guidance and mentor-ship throughout the training. His feedback and insights were invaluable in my development. I also want to thank Mr. Mrutu from the University of Dodoma for his assessments and support during my time at CODEBLOCK.
Lastly, I am very grateful to my family for their ongoing support and encouragement throughout this journey. I also appreciate my fellow students for their teamwork and collaboration, which made the experience even more rewarding. Thank you all for making this training a success.
















SUMMARY


During my fieldwork at CODEBLOCK, a software development organization focused on website and mobile app creation, I aimed to learn the React and Next.js frameworks. Through hands-on experience, I developed a portfolio showcasing my skills. This experience not only enhanced my technical abilities but also provided insights into modern web development practices, particularly in building high-performance applications using Next.js










                                                      

