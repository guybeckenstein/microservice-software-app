# Microservices Architecture with Docker: A Modular Approach for Diet and Meal Management
Developed a microservices-based architecture using `Docker` containers for a diet and meal management system.

The architecture consists of four services:
<li><strong>Diets</strong></li>
<li><strong>Meals</strong></li>
<li><strong>NGINX</strong></li>
<li><strong>MongoDB</strong></li>
<br>
Each service operates within its own package and contributes to the overall functionality. 

_Diets_ and _Meals_ are `Flask` applications, _NGINX_ acts as a `reverse-proxy server`, and _MongoDB_ is used as the `database`. 

The services are connected through a bridge network, enabling seamless communication and data management. 
The architecture offers scalability, modularity, and easy deployment, providing an efficient solution for managing diets and meals.

- This project is a part of an academic course "Software Engineering best practices for Cloud Native Applications"
