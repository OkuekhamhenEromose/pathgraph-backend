"""
Graph Repository — the ONLY layer that knows Cypher.
All queries are parameterized. No string interpolation.
"""

from typing import Optional, List, Dict, Any
from neo4j import Session
from app.core.exceptions import NotFoundError


class GraphRepository:
    """
    Encapsulates all CognoDB access.
    Methods map to domain operations, not database tables.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _node_to_dict(node) -> Optional[Dict[str, Any]]:
        """Convert a Neo4j node to a plain Python dict."""
        if node is None:
            return None
        return dict(node)

    # ─────────────────────────────────────────────
    # ROLE QUERIES
    # ─────────────────────────────────────────────

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Retrieve all job roles with their career track."""
        query = """
        MATCH (r:JobRole)
        OPTIONAL MATCH (r)-[:BELONGS_TO]->(t:CareerTrack)
        RETURN r, t.name as track_name
        ORDER BY r.level, r.title
        """
        result = self.session.run(query)
        roles = []
        for record in result:
            role = self._node_to_dict(record["r"])
            role["track_name"] = record["track_name"]
            roles.append(role)
        return roles

    def get_role_by_id(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single role by ID."""
        query = """
        MATCH (r:JobRole {id: $role_id})
        OPTIONAL MATCH (r)-[:BELONGS_TO]->(t:CareerTrack)
        RETURN r, t.name as track_name
        """
        result = self.session.run(query, role_id=role_id)
        record = result.single()
        if not record:
            return None
        role = self._node_to_dict(record["r"])
        role["track_name"] = record["track_name"]
        return role

    def get_role_skills(self, role_id: str) -> List[Dict[str, Any]]:
        """Retrieve skills required by a role, with requirement metadata."""
        query = """
        MATCH (r:JobRole {id: $role_id})
        MATCH (r)-[req:REQUIRES]->(s:Skill)
        RETURN s, req.level as level, req.proficiency_level as proficiency_level
        ORDER BY
            CASE req.level WHEN 'required' THEN 0 ELSE 1 END,
            s.name
        """
        result = self.session.run(query, role_id=role_id)
        skills = []
        for record in result:
            skill = self._node_to_dict(record["s"])
            skill["requirement_level"] = record["level"]
            skill["required_proficiency"] = record["proficiency_level"]
            skills.append(skill)
        return skills

    # ─────────────────────────────────────────────
    # SKILL QUERIES
    # ─────────────────────────────────────────────

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Retrieve all skills."""
        query = """
        MATCH (s:Skill)
        RETURN s
        ORDER BY s.category, s.name
        """
        result = self.session.run(query)
        return [self._node_to_dict(record["s"]) for record in result]

    def get_skill_by_id(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single skill by ID."""
        query = """
        MATCH (s:Skill {id: $skill_id})
        RETURN s
        """
        result = self.session.run(query, skill_id=skill_id)
        record = result.single()
        if not record:
            return None
        return self._node_to_dict(record["s"])

    def get_skill_prerequisites(self, skill_id: str) -> List[Dict[str, Any]]:
        """
        MULTI-HOP TRAVERSAL (1-5 hops):
        Find all prerequisite chains leading to a target skill.
        Returns every path from a root prerequisite to the target.
        """
        query = """
        MATCH path = (root:Skill)-[:PREREQUISITE_FOR*1..5]->(target:Skill {id: $skill_id})
        RETURN [node in nodes(path) | node {.*}] as path_nodes,
               length(path) as depth
        ORDER BY depth DESC
        """
        result = self.session.run(query, skill_id=skill_id)
        paths = []
        for record in result:
            paths.append({
                "path": record["path_nodes"],
                "depth": record["depth"]
            })
        return paths

    # ─────────────────────────────────────────────
    # PATH QUERIES (Multi-hop traversals)
    # ─────────────────────────────────────────────

    def find_career_path(self, from_role_id: str, to_role_id: str) -> Optional[Dict[str, Any]]:
        """
        MULTI-HOP TRAVERSAL (variable length):
        Find the shortest promotion path between two roles.
        Uses CognoDB's native shortestPath algorithm.
        """
        query = """
        MATCH path = shortestPath(
            (start:JobRole {id: $from_role_id})-[:PROMOTES_TO*1..10]->(end:JobRole {id: $to_role_id})
        )
        RETURN [node in nodes(path) | node {.*}] as roles,
               [rel in relationships(path) | rel {.*}] as promotions,
               length(path) as num_steps
        """
        result = self.session.run(query, from_role_id=from_role_id, to_role_id=to_role_id)
        record = result.single()
        if not record:
            return None
        return {
            "roles": record["roles"],
            "promotions": record["promotions"],
            "num_steps": record["num_steps"]
        }

    def get_person_skill_gaps(self, person_id: str, target_role_id: str) -> Dict[str, Any]:
        """
        RELATIONALLY AWKWARD QUERY:
        Find all skills missing for a target role, including missing prerequisites,
        and order them by prerequisite depth (topological approximation).

        In PostgreSQL this would require:
        - Recursive CTE for role requirements
        - Recursive CTE for skill prerequisites
        - Anti-join for skills the person has
        - Window functions for ordering

        In Cypher it is a single coherent graph traversal.
        """
        # Get current role
        current_role_query = """
        MATCH (p:Person {id: $person_id})-[:HOLDS_ROLE {is_current: true}]->(r:JobRole)
        RETURN r
        """
        current_result = self.session.run(current_role_query, person_id=person_id)
        current_record = current_result.single()
        current_role = self._node_to_dict(current_record["r"]) if current_record else None

        # Find missing required skills and their missing prerequisites
        gap_query = """
        MATCH (target:JobRole {id: $target_role_id})-[req:REQUIRES {level: 'required'}]->(req_skill:Skill)
        WHERE NOT (:Person {id: $person_id})-[:HAS_SKILL]->(req_skill)

        OPTIONAL MATCH (prereq:Skill)-[:PREREQUISITE_FOR*1..3]->(req_skill)
        WHERE NOT (:Person {id: $person_id})-[:HAS_SKILL]->(prereq)

        WITH req_skill, req, collect(DISTINCT prereq) as prereq_nodes
        RETURN req_skill,
               req.level as required_level,
               req.proficiency_level as required_proficiency,
               [p in prereq_nodes WHERE p IS NOT NULL | {name: p.name, id: p.id}] as prerequisites,
               size([p in prereq_nodes WHERE p IS NOT NULL]) as prereq_count
        ORDER BY prereq_count DESC, req_skill.difficulty ASC
        """
        result = self.session.run(gap_query, person_id=person_id, target_role_id=target_role_id)

        missing_skills = []
        for record in result:
            skill = self._node_to_dict(record["req_skill"])
            skill["required_level"] = record["required_level"]
            skill["required_proficiency"] = record["required_proficiency"]
            skill["prerequisites"] = record["prerequisites"]
            skill["prerequisite_depth"] = record["prereq_count"]
            missing_skills.append(skill)

        return {
            "current_role": current_role,
            "target_role_id": target_role_id,
            "missing_skills": missing_skills,
            "total_missing": len(missing_skills)
        }

    # ─────────────────────────────────────────────
    # TRACK QUERIES
    # ─────────────────────────────────────────────

    def get_all_tracks(self) -> List[Dict[str, Any]]:
        """Retrieve all career tracks."""
        query = """
        MATCH (t:CareerTrack)
        RETURN t
        ORDER BY t.name
        """
        result = self.session.run(query)
        return [self._node_to_dict(record["t"]) for record in result]

    def get_track_with_roles(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a career track with all roles belonging to it."""
        query = """
        MATCH (t:CareerTrack {id: $track_id})
        OPTIONAL MATCH (r:JobRole)-[:BELONGS_TO]->(t)
        RETURN t, collect(r) as roles
        """
        result = self.session.run(query, track_id=track_id)
        record = result.single()
        if not record:
            return None
        track = self._node_to_dict(record["t"])
        track["roles"] = sorted(
            [self._node_to_dict(r) for r in record["roles"] if r is not None],
            key=lambda x: x.get("level", 0)
        )
        return track

    # ─────────────────────────────────────────────
    # PERSON QUERIES
    # ─────────────────────────────────────────────

    def get_all_persons(self) -> List[Dict[str, Any]]:
        """Retrieve all people with their current role, if any."""
        query = """
        MATCH (p:Person)
        OPTIONAL MATCH (p)-[:HOLDS_ROLE {is_current: true}]->(r:JobRole)
        RETURN p, r
        ORDER BY p.name
        """
        result = self.session.run(query)
        persons = []
        for record in result:
            person = self._node_to_dict(record["p"])
            person["current_role"] = self._node_to_dict(record["r"])
            persons.append(person)
        return persons

    def get_person_by_id(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single person with their current role, if any."""
        query = """
        MATCH (p:Person {id: $person_id})
        OPTIONAL MATCH (p)-[:HOLDS_ROLE {is_current: true}]->(r:JobRole)
        RETURN p, r
        """
        result = self.session.run(query, person_id=person_id)
        record = result.single()
        if record is None:
            return None
        person = self._node_to_dict(record["p"])
        person["current_role"] = self._node_to_dict(record["r"])
        return person

    def get_person_skills(self, person_id: str) -> List[Dict[str, Any]]:
        """Retrieve all skills held by a person, with proficiency."""
        query = """
        MATCH (p:Person {id: $person_id})-[h:HAS_SKILL]->(s:Skill)
        RETURN s, h.proficiency_level as proficiency_level
        ORDER BY s.name
        """
        result = self.session.run(query, person_id=person_id)
        skills = []
        for record in result:
            skill = self._node_to_dict(record["s"])
            skill["proficiency_level"] = record["proficiency_level"]
            skills.append(skill)
        return skills
