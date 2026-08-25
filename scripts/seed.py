#!/usr/bin/env python3
"""
Seed script for PathGraph.
Creates a realistic, connected graph of career tracks, roles, skills, and people.
Run this after creating your CognoDB instance and configuring .env.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not URI or not PASSWORD:
    raise ValueError("Missing COGNODB_URI or COGNODB_PASSWORD in environment")


def clear_database(session):
    """Remove all existing nodes and relationships."""
    session.run("MATCH (n) DETACH DELETE n")
    print("Cleared existing data")


def create_tracks(session):
    """Create career tracks."""
    query = """
    CREATE (t1:CareerTrack {id: 'track-ic', name: 'Individual Contributor', description: 'Technical depth track'})
    CREATE (t2:CareerTrack {id: 'track-mgmt', name: 'Engineering Management', description: 'People leadership track'})
    """
    session.run(query)
    print("Created career tracks")


def create_roles(session):
    """Create job roles and promotion relationships."""
    query = """
    // IC Track Roles
    CREATE (jr:JobRole {id: 'r-jr', title: 'Junior Engineer', level: 1, category: 'general', typical_years_experience: 0})
    CREATE (eng:JobRole {id: 'r-eng', title: 'Engineer', level: 2, category: 'general', typical_years_experience: 2})
    CREATE (sr:JobRole {id: 'r-sr', title: 'Senior Engineer', level: 3, category: 'general', typical_years_experience: 5})
    CREATE (staff:JobRole {id: 'r-staff', title: 'Staff Engineer', level: 4, category: 'general', typical_years_experience: 8})
    CREATE (principal:JobRole {id: 'r-principal', title: 'Principal Engineer', level: 5, category: 'general', typical_years_experience: 12})

    // Backend Specialization
    CREATE (sr_be:JobRole {id: 'r-sr-be', title: 'Senior Backend Engineer', level: 3, category: 'backend', typical_years_experience: 5})
    CREATE (staff_be:JobRole {id: 'r-staff-be', title: 'Staff Backend Engineer', level: 4, category: 'backend', typical_years_experience: 8})

    // Frontend Specialization
    CREATE (sr_fe:JobRole {id: 'r-sr-fe', title: 'Senior Frontend Engineer', level: 3, category: 'frontend', typical_years_experience: 5})
    CREATE (staff_fe:JobRole {id: 'r-staff-fe', title: 'Staff Frontend Engineer', level: 4, category: 'frontend', typical_years_experience: 8})

    // DevOps
    CREATE (devops:JobRole {id: 'r-devops', title: 'DevOps Engineer', level: 3, category: 'devops', typical_years_experience: 5})
    CREATE (platform:JobRole {id: 'r-platform', title: 'Platform Engineer', level: 4, category: 'devops', typical_years_experience: 8})

    // Management Track
    CREATE (em:JobRole {id: 'r-em', title: 'Engineering Manager', level: 4, category: 'management', typical_years_experience: 7})
    CREATE (srem:JobRole {id: 'r-srem', title: 'Senior Engineering Manager', level: 5, category: 'management', typical_years_experience: 10})
    CREATE (director:JobRole {id: 'r-director', title: 'Director of Engineering', level: 6, category: 'management', typical_years_experience: 14})

    // Promotions (PROMOTES_TO relationships)
    CREATE (jr)-[:PROMOTES_TO {typical_years: 2, commonness: 0.9}]->(eng)
    CREATE (eng)-[:PROMOTES_TO {typical_years: 3, commonness: 0.8}]->(sr)
    CREATE (eng)-[:PROMOTES_TO {typical_years: 3, commonness: 0.6}]->(sr_be)
    CREATE (eng)-[:PROMOTES_TO {typical_years: 3, commonness: 0.5}]->(sr_fe)
    CREATE (sr)-[:PROMOTES_TO {typical_years: 3, commonness: 0.7}]->(staff)
    CREATE (sr_be)-[:PROMOTES_TO {typical_years: 3, commonness: 0.7}]->(staff_be)
    CREATE (sr_fe)-[:PROMOTES_TO {typical_years: 3, commonness: 0.7}]->(staff_fe)
    CREATE (staff)-[:PROMOTES_TO {typical_years: 4, commonness: 0.5}]->(principal)
    CREATE (staff_be)-[:PROMOTES_TO {typical_years: 4, commonness: 0.5}]->(principal)
    CREATE (staff_fe)-[:PROMOTES_TO {typical_years: 4, commonness: 0.4}]->(principal)
    CREATE (sr)-[:PROMOTES_TO {typical_years: 2, commonness: 0.4}]->(em)
    CREATE (sr_be)-[:PROMOTES_TO {typical_years: 2, commonness: 0.3}]->(em)
    CREATE (em)-[:PROMOTES_TO {typical_years: 3, commonness: 0.6}]->(srem)
    CREATE (srem)-[:PROMOTES_TO {typical_years: 4, commonness: 0.5}]->(director)
    CREATE (eng)-[:PROMOTES_TO {typical_years: 3, commonness: 0.4}]->(devops)
    CREATE (devops)-[:PROMOTES_TO {typical_years: 3, commonness: 0.6}]->(platform)

    // Track membership
    CREATE (jr)-[:BELONGS_TO {order: 1}]->(t1)
    CREATE (eng)-[:BELONGS_TO {order: 2}]->(t1)
    CREATE (sr)-[:BELONGS_TO {order: 3}]->(t1)
    CREATE (sr_be)-[:BELONGS_TO {order: 3}]->(t1)
    CREATE (sr_fe)-[:BELONGS_TO {order: 3}]->(t1)
    CREATE (staff)-[:BELONGS_TO {order: 4}]->(t1)
    CREATE (staff_be)-[:BELONGS_TO {order: 4}]->(t1)
    CREATE (staff_fe)-[:BELONGS_TO {order: 4}]->(t1)
    CREATE (principal)-[:BELONGS_TO {order: 5}]->(t1)
    CREATE (devops)-[:BELONGS_TO {order: 3}]->(t1)
    CREATE (platform)-[:BELONGS_TO {order: 4}]->(t1)

    CREATE (em)-[:BELONGS_TO {order: 1}]->(t2)
    CREATE (srem)-[:BELONGS_TO {order: 2}]->(t2)
    CREATE (director)-[:BELONGS_TO {order: 3}]->(t2)
    """
    session.run(query)
    print("Created job roles and promotion graph")


def create_skills(session):
    """Create skills and prerequisite chains."""
    query = """
    // Languages
    CREATE (python:Skill {id: 's-python', name: 'Python', category: 'language', difficulty: 2})
    CREATE (js:Skill {id: 's-js', name: 'JavaScript', category: 'language', difficulty: 2})
    CREATE (ts:Skill {id: 's-ts', name: 'TypeScript', category: 'language', difficulty: 3})
    CREATE (go:Skill {id: 's-go', name: 'Go', category: 'language', difficulty: 3})
    CREATE (sql:Skill {id: 's-sql', name: 'SQL', category: 'language', difficulty: 2})
    CREATE (bash:Skill {id: 's-bash', name: 'Bash', category: 'language', difficulty: 2})

    // Frameworks
    CREATE (react:Skill {id: 's-react', name: 'React', category: 'framework', difficulty: 3})
    CREATE (fastapi:Skill {id: 's-fastapi', name: 'FastAPI', category: 'framework', difficulty: 3})
    CREATE (django:Skill {id: 's-django', name: 'Django', category: 'framework', difficulty: 3})
    CREATE (nodejs:Skill {id: 's-nodejs', name: 'Node.js', category: 'framework', difficulty: 3})
    CREATE (graphql:Skill {id: 's-graphql', name: 'GraphQL', category: 'framework', difficulty: 4})
    CREATE (rest:Skill {id: 's-rest', name: 'REST APIs', category: 'framework', difficulty: 2})

    // Databases
    CREATE (postgres:Skill {id: 's-postgres', name: 'PostgreSQL', category: 'database', difficulty: 3})
    CREATE (mongo:Skill {id: 's-mongo', name: 'MongoDB', category: 'database', difficulty: 3})
    CREATE (redis:Skill {id: 's-redis', name: 'Redis', category: 'database', difficulty: 3})
    CREATE (neo4j_skill:Skill {id: 's-neo4j', name: 'Neo4j', category: 'database', difficulty: 4})

    // Tools
    CREATE (docker:Skill {id: 's-docker', name: 'Docker', category: 'tool', difficulty: 3})
    CREATE (k8s:Skill {id: 's-k8s', name: 'Kubernetes', category: 'tool', difficulty: 4})
    CREATE (aws:Skill {id: 's-aws', name: 'AWS', category: 'tool', difficulty: 3})
    CREATE (git:Skill {id: 's-git', name: 'Git', category: 'tool', difficulty: 2})
    CREATE (cicd:Skill {id: 's-cicd', name: 'CI/CD', category: 'tool', difficulty: 3})
    CREATE (terraform:Skill {id: 's-terraform', name: 'Terraform', category: 'tool', difficulty: 3})
    CREATE (linux:Skill {id: 's-linux', name: 'Linux', category: 'tool', difficulty: 2})

    // Paradigms
    CREATE (oop:Skill {id: 's-oop', name: 'OOP', category: 'paradigm', difficulty: 2})
    CREATE (fp:Skill {id: 's-fp', name: 'Functional Programming', category: 'paradigm', difficulty: 3})
    CREATE (microservices:Skill {id: 's-microservices', name: 'Microservices', category: 'paradigm', difficulty: 4})
    CREATE (event_driven:Skill {id: 's-event-driven', name: 'Event-Driven Architecture', category: 'paradigm', difficulty: 4})
    CREATE (sysdesign:Skill {id: 's-sysdesign', name: 'System Design', category: 'paradigm', difficulty: 5})
    CREATE (distributed:Skill {id: 's-distributed', name: 'Distributed Systems', category: 'paradigm', difficulty: 5})

    // Soft Skills
    CREATE (comm:Skill {id: 's-comm', name: 'Communication', category: 'soft_skill', difficulty: 2})
    CREATE (leadership:Skill {id: 's-leadership', name: 'Leadership', category: 'soft_skill', difficulty: 4})
    CREATE (mentoring:Skill {id: 's-mentoring', name: 'Mentoring', category: 'soft_skill', difficulty: 3})
    CREATE (problem_solving:Skill {id: 's-problem-solving', name: 'Problem Solving', category: 'soft_skill', difficulty: 2})

    // Domain
    CREATE (ml:Skill {id: 's-ml', name: 'Machine Learning', category: 'domain', difficulty: 5})
    CREATE (data_eng:Skill {id: 's-data-eng', name: 'Data Engineering', category: 'domain', difficulty: 4})
    CREATE (cloud_arch:Skill {id: 's-cloud-arch', name: 'Cloud Architecture', category: 'domain', difficulty: 5})
    CREATE (security:Skill {id: 's-security', name: 'Security Fundamentals', category: 'domain', difficulty: 4})

    // Prerequisites (DAG — acyclic)
    CREATE (js)-[:PREREQUISITE_FOR {strength: 0.9}]->(ts)
    CREATE (ts)-[:PREREQUISITE_FOR {strength: 0.9}]->(react)
    CREATE (python)-[:PREREQUISITE_FOR {strength: 0.9}]->(fastapi)
    CREATE (python)-[:PREREQUISITE_FOR {strength: 0.8}]->(django)
    CREATE (sql)-[:PREREQUISITE_FOR {strength: 0.9}]->(postgres)
    CREATE (sql)-[:PREREQUISITE_FOR {strength: 0.7}]->(mongo)
    CREATE (rest)-[:PREREQUISITE_FOR {strength: 0.8}]->(graphql)
    CREATE (rest)-[:PREREQUISITE_FOR {strength: 0.9}]->(microservices)
    CREATE (microservices)-[:PREREQUISITE_FOR {strength: 0.9}]->(sysdesign)
    CREATE (sysdesign)-[:PREREQUISITE_FOR {strength: 0.9}]->(distributed)
    CREATE (docker)-[:PREREQUISITE_FOR {strength: 0.9}]->(k8s)
    CREATE (k8s)-[:PREREQUISITE_FOR {strength: 0.8}]->(cloud_arch)
    CREATE (aws)-[:PREREQUISITE_FOR {strength: 0.7}]->(cloud_arch)
    CREATE (linux)-[:PREREQUISITE_FOR {strength: 0.8}]->(docker)
    CREATE (git)-[:PREREQUISITE_FOR {strength: 0.7}]->(cicd)
    CREATE (oop)-[:PREREQUISITE_FOR {strength: 0.7}]->(sysdesign)
    CREATE (security)-[:PREREQUISITE_FOR {strength: 0.8}]->(cloud_arch)
    CREATE (comm)-[:PREREQUISITE_FOR {strength: 0.9}]->(leadership)
    CREATE (leadership)-[:PREREQUISITE_FOR {strength: 0.9}]->(mentoring)
    CREATE (problem_solving)-[:PREREQUISITE_FOR {strength: 0.8}]->(sysdesign)
    CREATE (bash)-[:PREREQUISITE_FOR {strength: 0.6}]->(linux)
    CREATE (js)-[:PREREQUISITE_FOR {strength: 0.8}]->(nodejs)
    CREATE (ts)-[:PREREQUISITE_FOR {strength: 0.9}]->(nodejs)
    CREATE (python)-[:PREREQUISITE_FOR {strength: 0.7}]->(data_eng)
    CREATE (postgres)-[:PREREQUISITE_FOR {strength: 0.8}]->(data_eng)
    CREATE (oop)-[:PREREQUISITE_FOR {strength: 0.6}]->(fp)
    """
    session.run(query)
    print("Created skills and prerequisite chains")


def create_role_requirements(session):
    """Link roles to required skills."""
    query = """
    MATCH (jr:JobRole {id: 'r-jr'}), (eng:JobRole {id: 'r-eng'}), (sr:JobRole {id: 'r-sr'}),
          (staff:JobRole {id: 'r-staff'}), (principal:JobRole {id: 'r-principal'}),
          (sr_be:JobRole {id: 'r-sr-be'}), (staff_be:JobRole {id: 'r-staff-be'}),
          (sr_fe:JobRole {id: 'r-sr-fe'}), (staff_fe:JobRole {id: 'r-staff-fe'}),
          (devops:JobRole {id: 'r-devops'}), (platform:JobRole {id: 'r-platform'}),
          (em:JobRole {id: 'r-em'}), (srem:JobRole {id: 'r-srem'}), (director:JobRole {id: 'r-director'})

    MATCH (python:Skill {id: 's-python'}), (js:Skill {id: 's-js'}), (ts:Skill {id: 's-ts'}),
          (go:Skill {id: 's-go'}), (sql:Skill {id: 's-sql'}), (bash:Skill {id: 's-bash'}),
          (react:Skill {id: 's-react'}), (fastapi:Skill {id: 's-fastapi'}), (django:Skill {id: 's-django'}),
          (nodejs:Skill {id: 's-nodejs'}), (graphql:Skill {id: 's-graphql'}), (rest:Skill {id: 's-rest'}),
          (postgres:Skill {id: 's-postgres'}), (mongo:Skill {id: 's-mongo'}), (redis:Skill {id: 's-redis'}),
          (neo4j_skill:Skill {id: 's-neo4j'}),
          (docker:Skill {id: 's-docker'}), (k8s:Skill {id: 's-k8s'}), (aws:Skill {id: 's-aws'}),
          (git:Skill {id: 's-git'}), (cicd:Skill {id: 's-cicd'}), (terraform:Skill {id: 's-terraform'}),
          (linux:Skill {id: 's-linux'}),
          (oop:Skill {id: 's-oop'}), (fp:Skill {id: 's-fp'}), (microservices:Skill {id: 's-microservices'}),
          (event_driven:Skill {id: 's-event-driven'}), (sysdesign:Skill {id: 's-sysdesign'}),
          (distributed:Skill {id: 's-distributed'}),
          (comm:Skill {id: 's-comm'}), (leadership:Skill {id: 's-leadership'}), (mentoring:Skill {id: 's-mentoring'}),
          (problem_solving:Skill {id: 's-problem-solving'}),
          (ml:Skill {id: 's-ml'}), (data_eng:Skill {id: 's-data-eng'}), (cloud_arch:Skill {id: 's-cloud-arch'}),
          (security:Skill {id: 's-security'})

    // Junior Engineer
    CREATE (jr)-[:REQUIRES {level: 'required', proficiency_level: 2}]->(python)
    CREATE (jr)-[:REQUIRES {level: 'required', proficiency_level: 2}]->(js)
    CREATE (jr)-[:REQUIRES {level: 'required', proficiency_level: 2}]->(git)
    CREATE (jr)-[:REQUIRES {level: 'required', proficiency_level: 2}]->(problem_solving)
    CREATE (jr)-[:REQUIRES {level: 'required', proficiency_level: 2}]->(oop)
    CREATE (jr)-[:REQUIRES {level: 'preferred', proficiency_level: 1}]->(sql)
    CREATE (jr)-[:REQUIRES {level: 'preferred', proficiency_level: 1}]->(linux)

    // Engineer
    CREATE (eng)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(python)
    CREATE (eng)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(js)
    CREATE (eng)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(sql)
    CREATE (eng)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(rest)
    CREATE (eng)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(git)
    CREATE (eng)-[:REQUIRES {level: 'required', proficiency_level: 2}]->(cicd)
    CREATE (eng)-[:REQUIRES {level: 'preferred', proficiency_level: 2}]->(ts)
    CREATE (eng)-[:REQUIRES {level: 'preferred', proficiency_level: 2}]->(docker)

    // Senior Engineer
    CREATE (sr)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(ts)
    CREATE (sr)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(sysdesign)
    CREATE (sr)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(microservices)
    CREATE (sr)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(comm)
    CREATE (sr)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(cloud_arch)
    CREATE (sr)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(leadership)

    // Staff Engineer
    CREATE (staff)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(distributed)
    CREATE (staff)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(event_driven)
    CREATE (staff)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(leadership)
    CREATE (staff)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(mentoring)
    CREATE (staff)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(security)
    CREATE (staff)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(neo4j_skill)

    // Principal Engineer
    CREATE (principal)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(cloud_arch)
    CREATE (principal)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(security)
    CREATE (principal)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(mentoring)
    CREATE (principal)-[:REQUIRES {level: 'preferred', proficiency_level: 4}]->(ml)

    // Senior Backend Engineer
    CREATE (sr_be)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(python)
    CREATE (sr_be)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(postgres)
    CREATE (sr_be)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(redis)
    CREATE (sr_be)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(fastapi)
    CREATE (sr_be)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(sysdesign)
    CREATE (sr_be)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(mongo)
    CREATE (sr_be)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(event_driven)

    // Staff Backend Engineer
    CREATE (staff_be)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(distributed)
    CREATE (staff_be)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(event_driven)
    CREATE (staff_be)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(leadership)
    CREATE (staff_be)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(go)
    CREATE (staff_be)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(neo4j_skill)

    // Senior Frontend Engineer
    CREATE (sr_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(js)
    CREATE (sr_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(ts)
    CREATE (sr_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(react)
    CREATE (sr_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(rest)
    CREATE (sr_fe)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(sysdesign)
    CREATE (sr_fe)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(graphql)

    // Staff Frontend Engineer
    CREATE (staff_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(graphql)
    CREATE (staff_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(leadership)
    CREATE (staff_fe)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(mentoring)
    CREATE (staff_fe)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(cloud_arch)

    // DevOps Engineer
    CREATE (devops)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(linux)
    CREATE (devops)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(docker)
    CREATE (devops)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(k8s)
    CREATE (devops)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(aws)
    CREATE (devops)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(terraform)
    CREATE (devops)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(cicd)
    CREATE (devops)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(python)
    CREATE (devops)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(security)

    // Platform Engineer
    CREATE (platform)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(distributed)
    CREATE (platform)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(event_driven)
    CREATE (platform)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(security)
    CREATE (platform)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(go)
    CREATE (platform)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(neo4j_skill)
    CREATE (platform)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(cloud_arch)

    // Engineering Manager
    CREATE (em)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(comm)
    CREATE (em)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(leadership)
    CREATE (em)-[:REQUIRES {level: 'required', proficiency_level: 4}]->(mentoring)
    CREATE (em)-[:REQUIRES {level: 'required', proficiency_level: 3}]->(sysdesign)
    CREATE (em)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(microservices)
    CREATE (em)-[:REQUIRES {level: 'preferred', proficiency_level: 3}]->(cloud_arch)

    // Senior Engineering Manager
    CREATE (srem)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(distributed)
    CREATE (srem)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(cloud_arch)
    CREATE (srem)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(mentoring)
    CREATE (srem)-[:REQUIRES {level: 'preferred', proficiency_level: 4}]->(security)
    CREATE (srem)-[:REQUIRES {level: 'preferred', proficiency_level: 4}]->(event_driven)

    // Director of Engineering
    CREATE (director)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(security)
    CREATE (director)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(ml)
    CREATE (director)-[:REQUIRES {level: 'required', proficiency_level: 5}]->(cloud_arch)
    CREATE (director)-[:REQUIRES {level: 'preferred', proficiency_level: 4}]->(distributed)
    """
    session.run(query)
    print("Created role-skill requirements")


def create_people(session):
    """Create example people with skills and current roles."""
    query = """
    CREATE (alex:Person {id: 'p-alex', name: 'Alex Chen', email: 'alex@example.com', years_of_experience: 4, location: 'San Francisco'})
    CREATE (jordan:Person {id: 'p-jordan', name: 'Jordan Smith', email: 'jordan@example.com', years_of_experience: 3, location: 'New York'})
    CREATE (taylor:Person {id: 'p-taylor', name: 'Taylor Wong', email: 'taylor@example.com', years_of_experience: 6, location: 'London'})
    CREATE (morgan:Person {id: 'p-morgan', name: 'Morgan Lee', email: 'morgan@example.com', years_of_experience: 5, location: 'Seattle'})

    // Alex: Senior Backend Engineer
    CREATE (alex)-[:HOLDS_ROLE {since: '2024-01-15', is_current: true}]->(:JobRole {id: 'r-sr-be'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 5, years_experience: 4}]->(:Skill {id: 's-python'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-postgres'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-redis'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 4, years_experience: 2}]->(:Skill {id: 's-fastapi'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 5, years_experience: 4}]->(:Skill {id: 's-git'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-docker'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 4, years_experience: 4}]->(:Skill {id: 's-linux'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 5, years_experience: 4}]->(:Skill {id: 's-rest'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-js'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 5, years_experience: 4}]->(:Skill {id: 's-sql'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 3, years_experience: 3}]->(:Skill {id: 's-oop'})
    CREATE (alex)-[:HAS_SKILL {proficiency: 2, years_experience: 1}]->(:Skill {id: 's-sysdesign'})

    // Jordan: Software Engineer (frontend-leaning)
    CREATE (jordan)-[:HOLDS_ROLE {since: '2023-06-01', is_current: true}]->(:JobRole {id: 'r-eng'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-js'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-ts'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 4, years_experience: 2}]->(:Skill {id: 's-react'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 5, years_experience: 3}]->(:Skill {id: 's-git'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 4, years_experience: 2}]->(:Skill {id: 's-rest'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 3, years_experience: 1}]->(:Skill {id: 's-sql'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 2, years_experience: 1}]->(:Skill {id: 's-docker'})
    CREATE (jordan)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-comm'})

    // Taylor: Senior Software Engineer
    CREATE (taylor)-[:HOLDS_ROLE {since: '2023-03-10', is_current: true}]->(:JobRole {id: 'r-sr'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 5, years_experience: 6}]->(:Skill {id: 's-python'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 5, years_experience: 5}]->(:Skill {id: 's-js'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-ts'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-react'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 4, years_experience: 4}]->(:Skill {id: 's-sql'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 5, years_experience: 5}]->(:Skill {id: 's-rest'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 5, years_experience: 6}]->(:Skill {id: 's-git'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-docker'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 3, years_experience: 1}]->(:Skill {id: 's-microservices'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-comm'})
    CREATE (taylor)-[:HAS_SKILL {proficiency: 2, years_experience: 1}]->(:Skill {id: 's-sysdesign'})

    // Morgan: DevOps Engineer
    CREATE (morgan)-[:HOLDS_ROLE {since: '2023-09-01', is_current: true}]->(:JobRole {id: 'r-devops'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 5, years_experience: 5}]->(:Skill {id: 's-linux'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 5, years_experience: 4}]->(:Skill {id: 's-docker'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-k8s'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 4, years_experience: 3}]->(:Skill {id: 's-aws'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-terraform'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 4, years_experience: 4}]->(:Skill {id: 's-cicd'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 3, years_experience: 2}]->(:Skill {id: 's-python'})
    CREATE (morgan)-[:HAS_SKILL {proficiency: 5, years_experience: 5}]->(:Skill {id: 's-git'})
    """
    session.run(query)
    print("Created people with skills and roles")


def seed():
    """Main seeding orchestrator."""
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    try:
        with driver.session() as session:
            clear_database(session)
            create_tracks(session)
            create_roles(session)
            create_skills(session)
            create_role_requirements(session)
            create_people(session)
        print("\nSeed complete! Graph populated with:")
        print("  - 2 Career Tracks")
        print("  - 13 Job Roles")
        print("  - 32 Skills")
        print("  - 4 Example People")
        print("  - Promotion, prerequisite, and requirement relationships")
    finally:
        driver.close()


if __name__ == "__main__":
    print("Seeding PathGraph database...")
    seed()
