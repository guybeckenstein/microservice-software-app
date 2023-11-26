# Microservices Architecture with Docker: A Modular Approach for Diet and Meal Management
Developed a SaaS microservices-based architecture using Docker containers for a diet and meal management system, using `API Ninjas Recipe` – can make up to 50,000 API calls per month.

The architecture consists of four services:
<li><strong>Diets</strong></li>
<li><strong>Meals</strong></li>
<li><strong>NGINX</strong></li>
<li><strong>MongoDB</strong></li>
<br>
Diets and Meals are Flask applications, NGINX acts as a reverse-proxy server (for GET requests), and MongoDB is used as the database.
<br>
docker-compose YAML file was also used.

The services are connected through a bridge network, enabling seamless communication and data management. 
The architecture offers scalability, modularity, and easy deployment, providing an efficient solution for managing diets and meals.

- This project is a part of an academic course "Software Engineering best practices for Cloud Native Applications"
