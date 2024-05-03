import os
import logging

from sqlalchemy import Column, String, ForeignKey, create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from src.utils import get_base_path

Base = declarative_base()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class JobCandidateAssociation(Base):
    __tablename__ = 'job_candidate_association'
    job_id = Column(String, ForeignKey('jobs.id'), primary_key=True)
    candidate_id = Column(String, ForeignKey('candidates.id'), primary_key=True)
    motivation = Column(String)  # This field stores the motivation for each specific Job-Candidate pair

    # Relationship to Job and Candidate
    job = relationship("JobModel", back_populates="candidates")
    candidate = relationship("CandidateModel", back_populates="jobs")


class ContactModel(Base):
    __tablename__ = 'contacts'
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    jobs = relationship("JobModel", order_by="JobModel.id", back_populates="submitter")  # Corrected reference to JobModel


class ContactDAO:
    def __init__(self, session):
        self.session = session

    def add_contact(self, contact):
        try:
            # Disable autoflush to control when the session is flushed
            with self.session.no_autoflush:
                contact_model = self.session.query(ContactModel).filter_by(id=contact.id).first()
            
            if contact_model is None:
                self.session.add(contact)
                self.session.commit()
                logging.info(f"Contact {contact.id} added successfully.")
            else:
                logging.info(f"Contact {contact.id} already exists, skipping addition.")

        except IntegrityError as e:
            logging.error(f"Integrity Error: Attempt to add a duplicate contact {contact.id} - {str(e)}")
            self.session.rollback()  # Roll back in case of integrity error

        except Exception as e:
            logging.error(f"Failed to add contact {contact.id}: {str(e)}")
            self.session.rollback()

    def get_contact_by_id(self, contact_id):
        return self.session.query(ContactModel).filter_by(id=contact_id).first()

    def update_contact(self, contact):
        existing_contact = self.session.query(ContactModel).filter_by(id=contact.id).first()
        if existing_contact:
            existing_contact.name = contact.name
            existing_contact.email = contact.email
            existing_contact.phone = contact.phone
            self.session.commit()

    def delete_contact(self, contact_id):
        contact = self.session.query(ContactModel).filter_by(id=contact_id).first()
        if contact:
            self.session.delete(contact)
            self.session.commit()

    def list_all_contacts(self):
        return self.session.query(ContactModel).all()


class AssignmentModel(Base):
    __tablename__ = 'assignments'
    id = Column(String, primary_key=True)
    skills = Column(String)
    requirements = Column(String)
    preferences = Column(String)
    jobs = relationship("JobModel", order_by="JobModel.id", back_populates="assignment")  # Corrected reference to JobModel

class AssignmentDAO:
    def __init__(self, session):
        self.session = session

    def add_assignment(self, assignment):
        self.session.add(assignment)
        self.session.commit()

    def get_assignment_by_id(self, assignment_id):
        return self.session.query(AssignmentModel).filter_by(id=assignment_id).first()

    def update_assignment(self, assignment):
        assignment_model = self.session.query(AssignmentModel).filter_by(id=assignment.id).first()
        if assignment_model:
            assignment_model.skills = assignment.skills
            assignment_model.requirements = assignment.requirements
            assignment_model.preferences = assignment.preferences
            self.session.commit()

    def delete_assignment(self, assignment_id):
        assignment = self.session.query(AssignmentModel).filter_by(id=assignment_id).first()
        if assignment:
            self.session.delete(assignment)
            self.session.commit()

    def list_all_assignments(self):
        return self.session.query(AssignmentModel).all()

class JobModel(Base):
    __tablename__ = 'jobs'
    id = Column(String, primary_key=True)
    url = Column(String)
    position = Column(String)
    company = Column(String)
    commitment = Column(String)
    start = Column(String)
    location = Column(String)
    max_hourly_rate = Column(String)
    end = Column(String)
    deadline = Column(String)
    status = Column(String)
    contact_id = Column(String, ForeignKey('contacts.id'))  # Match the data type of ContactModel.id
    submitter = relationship("ContactModel", back_populates="jobs")  # Corrected reference to ContactModel
    assignment_id = Column(String, ForeignKey('assignments.id'))  # Match the data type of AssignmentModel.id
    assignment = relationship("AssignmentModel", back_populates="jobs")  # Corrected reference to AssignmentModel

    candidates = relationship("JobCandidateAssociation", back_populates="job")

class JobDAO:
    def __init__(self):
        self.session = Session()

    def add_job(self, job):
        try:
            if self.session.is_active:
                self.session.commit()

            with self.session.begin():
                job_model = self.session.query(JobModel).filter_by(id=job.id).first()
                if not job_model:
                    contact = self.session.query(ContactModel).filter_by(id=job.submitter.id).first() if job.submitter else None
                    
                    if not contact and job.submitter:
                        contact = ContactModel(
                            id=job.submitter.id, 
                            name=job.submitter.name, 
                            email=job.submitter.email, 
                            phone=job.submitter.phone
                        )
                        self.session.add(contact)
                    
                    assignment = self.session.query(AssignmentModel).filter_by(id=job.assignment.id).first() if job.assignment else None
                    if not assignment and job.assignment:
                        assignment = AssignmentModel(
                            id=job.assignment.id, 
                            skills=job.assignment.skills, 
                            requirements=job.assignment.requirements, 
                            preferences=job.assignment.preferences
                        )
                        self.session.add(assignment)

                    candidates = []
                    for candidate in job.candidates:
                        candidate_model = self.session.query(CandidateModel).filter_by(id=candidate.id).first()
                        if not candidate_model:
                            candidate_model = CandidateModel(
                                id=candidate.id, 
                                name=candidate.name, 
                                interests=candidate.interests, 
                                experience=candidate.experience, 
                                skills=candidate.skills, 
                                education=candidate.education, 
                                profile=candidate.profile, 
                                certificates=candidate.certificates
                            )
                            self.session.add(candidate_model)
                        candidates.append(candidate_model)

                    job_model = JobModel(
                        id=job.id,
                        url=job.url,
                        position=job.position,
                        company=job.company,
                        commitment=job._commitment,
                        start=job.start,
                        location=job.location,
                        max_hourly_rate=job.max_hourly_rate,
                        end=job.end,
                        deadline=job.deadline,
                        status=job.status,
                        submitter=contact,
                        assignment=assignment,
                        candidates=candidates,
                    )
                    self.session.add(job_model)

        except SQLAlchemyError as e:
            logging.error(f"Failed to add job {job.id}: {str(e)}")

    def update_job(self, job):
        job_model = self.session.query(JobModel).filter_by(id=job.id).first()
        if job_model:
            job_model.position = job.position
            job_model.company = job.company
            job_model.commitment = job.commitment
            job_model.start = job.start
            job_model.location = job.location
            job_model.max_hourly_rate = job.max_hourly_rate
            job_model.end = job.end
            job_model.deadline = job.deadline
            job_model.status = job.status

            try:
                if self.session.is_active:
                    self.session.commit()

                with self.session.begin():
                    if job.submitter:
                        contact = self.session.query(ContactModel).filter_by(id=job.submitter.id).first()
                        if not contact:
                            contact = ContactModel(
                                id=job.submitter.id, name=job.submitter.name, 
                                email=job.submitter.email, phone=job.submitter.phone
                            )
                            self.session.add(contact)
                        job_model.submitter = contact

                    if job.assignment:
                        assignment = self.session.query(AssignmentModel).filter_by(id=job.assignment.id).first()
                        if not assignment:
                            assignment = AssignmentModel(
                                id=job.assignment.id, skills=job.assignment.skills, 
                                requirements=job.assignment.requirements, preferences=job.assignment.preferences
                            )
                            self.session.add(assignment)
                        job_model.assignment = assignment
                    candidates = []
                    for candidate in job.candidates:
                        candidate_model = self.session.query(CandidateModel).filter_by(id=candidate.id).first()

                        if not candidate_model:
                            candidate_model = CandidateModel(
                                id=candidate.id, name=candidate.name, interests=candidate.interests, 
                                experience=candidate.experience, skills=candidate.skills, 
                                education=candidate.education, profile=candidate.profile, 
                                certificates=candidate.certificates
                            )
                            self.session.add(candidate_model)
                        candidates.append(candidate_model)
                    job_model.candidates = candidates

            except SQLAlchemyError as e:
                logging.error(f"Failed to update job {job.id}: {str(e)}")

    def get_job_by_id(self, job_id):
        job_model = self.session.query(JobModel).filter_by(id=job_id).first()
        if job_model:
            return job_model

    def delete_job(self, job_id):
        job_model = self.session.query(JobModel).filter_by(id=job_id).first()
        if job_model:
            self.session.delete(job_model)
            self.session.commit()

    def list_all_jobs(self):
        return self.session.query(JobModel).all()
    
    def get_job_by_id(self, job_id):
            return self.session.query(JobModel).filter_by(id=job_id).first()


class CandidateModel(Base):
    __tablename__ = 'candidates'
    id = Column(String, primary_key=True)
    name = Column(String)
    interests = Column(String)
    experience = Column(String)
    skills = Column(String)
    education = Column(String)
    profile = Column(String)
    certificates = Column(String)
    jobs = relationship("JobCandidateAssociation", back_populates="candidate")

class CandidateDAO:
    def __init__(self):
        self.session = Session()

    def add_candidate(self, candidate):
        candidate_model = self.session.query(CandidateModel).filter_by(id=candidate.id).first()
        if not candidate_model:
            candidate_model = CandidateModel(id=candidate.id, name=candidate.name, interests=candidate.interests, experience=candidate.experience, skills=candidate.skills, education=candidate.education, profile=candidate.profile, certificates=candidate.certificates)
            self.session.add(candidate_model)
            self.session.commit()
        else:
            logging.info(f'Candidate with ID {candidate.id} already exists in the database.')
            self.update_candidate(candidate)

    def update_candidate(self, candidate):
        candidate_model = self.session.query(CandidateModel).filter_by(id=candidate.id).first()
        if candidate_model:
            candidate_model.name = candidate.name
            candidate_model.interests = candidate.interests
            candidate_model.experience = candidate.experience
            candidate_model.skills = candidate.skills
            candidate_model.education = candidate.education
            candidate_model.profile = candidate.profile
            candidate_model.certificates = candidate.certificates
            self.session.commit()

    def get_candidate_by_id(self, candidate_id):
        return self.session.query(CandidateModel).filter_by(id=candidate_id).first()

    def delete_candidate(self, candidate_id):
        candidate_model = self.session.query(CandidateModel).filter_by(id=candidate_id).first()
        if candidate_model:
            self.session.delete(candidate_model)
            self.session.commit()

    def list_all_candidates(self):
        return self.session.query(CandidateModel).all()
        
    def get_motivation(self, job_id, candidate_id):
            association = self.session.query(JobCandidateAssociation).filter_by(
                job_id=job_id, candidate_id=candidate_id).first()
            if association:
                return association.motivation
            return None


class MatchDAO:
    def __init__(self):
        self.session = Session()

    def add_match(self, job_id, candidate_id, motivation_text):
        motivation_model = self.session.query(JobCandidateAssociation).filter_by(job_id=job_id, candidate_id=candidate_id).first()
        if motivation_model:
            self.update_motivation(job_id, candidate_id, motivation_text)
        else:
            association = JobCandidateAssociation(
                job_id=job_id,
                candidate_id=candidate_id,
                motivation=motivation_text
            )
            self.session.add(association)
            self.session.commit()

    def update_motivation(self, job_id, candidate_id, new_motivation_text):
        association = self.session.query(JobCandidateAssociation).filter_by(
            job_id=job_id, candidate_id=candidate_id).first()
        if association:
            association.motivation = new_motivation_text
            self.session.commit()

    def get_match(self, job_id, candidate_id):
        return self.session.query(JobCandidateAssociation).filter_by(
            job_id=job_id, candidate_id=candidate_id).first()

    def delete_match(self, job_id, candidate_id):
        association = self.session.query(JobCandidateAssociation).filter_by(
            job_id=job_id, candidate_id=candidate_id).first()
        if association:
            self.session.delete(association)
            self.session.commit()

    def list_all_matches(self):
        return self.session.query(JobCandidateAssociation).all()
    
    def get_candidates_for_job(self, job_id):
            associations = self.session.query(JobCandidateAssociation).filter_by(job_id=job_id).all()
            candidates = [assoc.candidate for assoc in associations if assoc.candidate is not None]
            return candidates
    
    def get_motivation(self, job_id, candidate_id):
            association = self.session.query(JobCandidateAssociation).filter_by(
                job_id=job_id, candidate_id=candidate_id).first()
            if association:
                return association.motivation
            return None

# Set up the engine and session
engine_path = os.path.join(get_base_path(), 'db/_data/jobs.db')
engine = create_engine(engine_path)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

