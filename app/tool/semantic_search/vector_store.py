"""
Enhanced Vector Store for JobPilot-OpenManus
Production-ready vector storage and retrieval for semantic job search.
"""

import hashlib
import json
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.models import JobListing, JobEmbedding, JobMatch
from app.data.database import DatabaseManager

logger = logging.getLogger(__name__)


class VectorStore:
    """Production-ready vector storage and retrieval system."""
    
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 storage_backend: str = "chroma",
                 db_manager: Optional[DatabaseManager] = None):
        """Initialize the vector store.
        
        Args:
            embedding_model: Name of the sentence transformer model
            storage_backend: 'chroma', 'simple', or 'pinecone' (future)
            db_manager: Database manager for storing embeddings
        """
        self.embedding_model_name = embedding_model
        self.storage_backend = storage_backend
        self.db_manager = db_manager
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.dimension}")
        
        # Initialize storage backend
        self.storage = self._initialize_storage(storage_backend)
        
    def _initialize_storage(self, backend: str):
        """Initialize the chosen storage backend."""
        if backend == "chroma":
            return self._initialize_chroma()
        elif backend == "simple":
            return self._initialize_simple_storage()
        elif backend == "pinecone":
            # Future implementation
            raise NotImplementedError("Pinecone backend not yet implemented")
        else:
            raise ValueError(f"Unknown storage backend: {backend}")
    
    def _initialize_chroma(self):
        """Initialize Chroma vector database."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create Chroma client with persistent storage
            chroma_path = "data/chroma_db"
            os.makedirs(chroma_path, exist_ok=True)
            
            client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection for job embeddings
            collection = client.get_or_create_collection(
                name="job_embeddings",
                metadata={"description": "Job listing embeddings for semantic search"}
            )
            
            logger.info("Initialized Chroma vector database")
            return {"client": client, "collection": collection}
            
        except ImportError:
            logger.warning("Chroma not available, falling back to simple storage")
            return self._initialize_simple_storage()
    
    def _initialize_simple_storage(self):
        """Initialize simple in-memory storage (fallback)."""
        logger.info("Initialized simple in-memory vector storage")
        return {"embeddings": {}, "metadata": {}}
    
    def _create_content_hash(self, content: str) -> str:
        """Create a hash of content for change detection."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _extract_searchable_content(self, job: JobListing) -> str:
        """Extract searchable content from a job listing."""
        content_parts = []
        
        if job.title:
            content_parts.append(f"Title: {job.title}")
        if job.company:
            content_parts.append(f"Company: {job.company}")
        if job.description:
            content_parts.append(f"Description: {job.description}")
        if job.requirements:
            content_parts.append(f"Requirements: {job.requirements}")
        if job.responsibilities:
            content_parts.append(f"Responsibilities: {job.responsibilities}")
        if job.skills_required:
            content_parts.append(f"Required Skills: {', '.join(job.skills_required)}")
        if job.skills_preferred:
            content_parts.append(f"Preferred Skills: {', '.join(job.skills_preferred)}")
        if job.tech_stack:
            content_parts.append(f"Tech Stack: {', '.join(job.tech_stack)}")
        
        return " ".join(content_parts)
    
    async def store_job_embedding(self, job: JobListing) -> JobEmbedding:
        """Create and store embedding for a job listing."""
        try:
            # Extract content and create hash
            content = self._extract_searchable_content(job)
            content_hash = self._create_content_hash(content)
            
            # Check if we already have an embedding for this content
            if self.db_manager:
                with self.db_manager.get_session() as session:
                    existing_embedding = session.query(JobEmbeddingDB).filter(
                        JobEmbeddingDB.job_id == str(job.id),
                        JobEmbeddingDB.content_hash == content_hash
                    ).first()
                    
                    if existing_embedding:
                        logger.debug(f"Using existing embedding for job {job.id}")
                        return sqlalchemy_to_pydantic(existing_embedding, JobEmbedding)
            
            # Generate embedding
            logger.debug(f"Generating embedding for job {job.id}")
            embedding_vector = self.embedding_model.encode([content])[0].tolist()
            
            # Create embedding record
            job_embedding = JobEmbedding(
                job_id=job.id,
                embedding_model=self.embedding_model_name,
                content_hash=content_hash,
                embedding_vector=embedding_vector,
                embedding_dimension=self.dimension,
                content_type="job_description"
            )
            
            # Store in vector database
            await self._store_embedding_in_backend(job_embedding, job, content)
            
            # Store in SQL database if available
            if self.db_manager:
                with self.db_manager.get_session() as session:
                    from app.data.models import JobEmbeddingDB, pydantic_to_sqlalchemy
                    embedding_db = pydantic_to_sqlalchemy(job_embedding, JobEmbeddingDB)
                    session.add(embedding_db)
                    session.commit()
            
            logger.info(f"Stored embedding for job {job.id}")
            return job_embedding
            
        except Exception as e:
            logger.error(f"Failed to store embedding for job {job.id}: {e}")
            raise
    
    async def _store_embedding_in_backend(self, embedding: JobEmbedding, job: JobListing, content: str):
        """Store embedding in the chosen backend."""
        if self.storage_backend == "chroma":
            collection = self.storage["collection"]
            collection.add(
                embeddings=[embedding.embedding_vector],
                documents=[content],
                metadatas=[{
                    "job_id": str(embedding.job_id),
                    "title": job.title,
                    "company": job.company,
                    "location": job.location or "",
                    "job_type": job.job_type.value if job.job_type else "",
                    "remote_type": job.remote_type.value if job.remote_type else "",
                    "salary_min": job.salary_min or 0,
                    "salary_max": job.salary_max or 0,
                    "content_hash": embedding.content_hash,
                    "created_at": embedding.created_at.isoformat()
                }],
                ids=[str(embedding.job_id)]
            )
        else:  # Simple storage
            self.storage["embeddings"][str(embedding.job_id)] = embedding.embedding_vector
            self.storage["metadata"][str(embedding.job_id)] = {
                "job": job,
                "content": content,
                "embedding": embedding
            }
    
    async def batch_store_embeddings(self, jobs: List[JobListing]) -> List[JobEmbedding]:
        """Efficiently embed and store multiple jobs."""
        embeddings = []
        
        # Process jobs in batches for efficiency
        batch_size = 10
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            batch_embeddings = await asyncio.gather(*[
                self.store_job_embedding(job) for job in batch
            ])
            embeddings.extend(batch_embeddings)
            
            # Log progress
            if len(embeddings) % 50 == 0:
                logger.info(f"Processed {len(embeddings)}/{len(jobs)} job embeddings")
        
        logger.info(f"Completed batch embedding of {len(jobs)} jobs")
        return embeddings
    
    async def find_similar_jobs(self, 
                              query: str, 
                              filters: Optional[Dict[str, Any]] = None,
                              limit: int = 20,
                              similarity_threshold: float = 0.0) -> List[JobMatch]:
        """Find semantically similar jobs using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            if self.storage_backend == "chroma":
                return await self._search_chroma(query_embedding, filters, limit, similarity_threshold)
            else:
                return await self._search_simple(query_embedding, filters, limit, similarity_threshold)
                
        except Exception as e:
            logger.error(f"Failed to find similar jobs for query '{query}': {e}")
            return []
    
    async def _search_chroma(self, query_embedding: np.ndarray, filters: Optional[Dict[str, Any]], 
                           limit: int, similarity_threshold: float) -> List[JobMatch]:
        """Search using Chroma backend."""
        collection = self.storage["collection"]
        
        # Build filter conditions
        where_conditions = {}
        if filters:
            for key, value in filters.items():
                if key in ["job_type", "remote_type", "company"]:
                    where_conditions[key] = value
                elif key == "salary_min" and value:
                    where_conditions["salary_max"] = {"$gte": value}
                elif key == "salary_max" and value:
                    where_conditions["salary_min"] = {"$lte": value}
        
        # Perform similarity search
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(limit, 100),
            where=where_conditions if where_conditions else None,
            include=["metadatas", "documents", "distances"]
        )
        
        job_matches = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, job_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                similarity_score = 1 - distance  # Convert distance to similarity
                
                if similarity_score >= similarity_threshold:
                    metadata = results["metadatas"][0][i]
                    
                    # Create JobMatch with basic scoring
                    job_match = JobMatch(
                        job_id=job_id,
                        user_profile_id="",  # Will be set by caller
                        overall_score=similarity_score,
                        skills_match_score=similarity_score,
                        experience_match_score=0.5,  # Default
                        location_match_score=0.5,   # Default
                        salary_match_score=0.5,     # Default
                        match_reasons=[f"Semantic similarity: {similarity_score:.2f}"],
                        calculated_at=datetime.utcnow()
                    )
                    job_matches.append(job_match)
        
        return sorted(job_matches, key=lambda x: x.overall_score, reverse=True)
    
    async def _search_simple(self, query_embedding: np.ndarray, filters: Optional[Dict[str, Any]], 
                           limit: int, similarity_threshold: float) -> List[JobMatch]:
        """Search using simple in-memory storage."""
        if not self.storage["embeddings"]:
            return []
        
        job_matches = []
        
        for job_id, embedding_vector in self.storage["embeddings"].items():
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [query_embedding], 
                [np.array(embedding_vector)]
            )[0][0]
            
            if similarity >= similarity_threshold:
                metadata = self.storage["metadata"][job_id]
                job = metadata["job"]
                
                # Apply filters if provided
                if filters and not self._job_matches_filters(job, filters):
                    continue
                
                job_match = JobMatch(
                    job_id=job_id,
                    user_profile_id="",  # Will be set by caller
                    overall_score=float(similarity),
                    skills_match_score=float(similarity),
                    experience_match_score=0.5,
                    location_match_score=0.5,
                    salary_match_score=0.5,
                    match_reasons=[f"Semantic similarity: {similarity:.2f}"],
                    calculated_at=datetime.utcnow()
                )
                job_matches.append(job_match)
        
        # Sort by similarity score and limit results
        job_matches.sort(key=lambda x: x.overall_score, reverse=True)
        return job_matches[:limit]
    
    def _job_matches_filters(self, job: JobListing, filters: Dict[str, Any]) -> bool:
        """Check if a job matches the provided filters."""
        for key, value in filters.items():
            if key == "job_type" and job.job_type and job.job_type.value != value:
                return False
            elif key == "remote_type" and job.remote_type and job.remote_type.value != value:
                return False
            elif key == "company" and job.company.lower() != value.lower():
                return False
            elif key == "salary_min" and job.salary_max and job.salary_max < value:
                return False
            elif key == "salary_max" and job.salary_min and job.salary_min > value:
                return False
        
        return True
    
    async def hybrid_search(self, 
                           query: str,
                           keyword_weight: float = 0.3,
                           semantic_weight: float = 0.7,
                           filters: Optional[Dict[str, Any]] = None,
                           limit: int = 20) -> List[JobMatch]:
        """Combine keyword and semantic search with weighted scoring."""
        # For now, return semantic search results
        # TODO: Implement true hybrid search with keyword matching
        semantic_matches = await self.find_similar_jobs(query, filters, limit)
        
        # Adjust scores based on weights
        for match in semantic_matches:
            match.overall_score = match.overall_score * semantic_weight
            # Add keyword matching score when implemented
        
        return semantic_matches
    
    async def update_job_embedding(self, job_id: str) -> Optional[JobEmbedding]:
        """Update embedding when job content changes."""
        if not self.db_manager:
            logger.warning("Cannot update embedding without database manager")
            return None
        
        try:
            with self.db_manager.get_session() as session:
                from app.data.models import JobListingDB, sqlalchemy_to_pydantic
                
                # Get the updated job
                job_db = session.query(JobListingDB).filter(JobListingDB.id == job_id).first()
                if not job_db:
                    logger.warning(f"Job {job_id} not found")
                    return None
                
                job = sqlalchemy_to_pydantic(job_db, JobListing)
                
                # Delete old embedding
                await self.delete_job_embedding(job_id)
                
                # Create new embedding
                return await self.store_job_embedding(job)
                
        except Exception as e:
            logger.error(f"Failed to update embedding for job {job_id}: {e}")
            return None
    
    async def delete_job_embedding(self, job_id: str) -> bool:
        """Remove job embedding from vector store and database."""
        try:
            # Remove from vector storage
            if self.storage_backend == "chroma":
                collection = self.storage["collection"]
                try:
                    collection.delete(ids=[job_id])
                except Exception as e:
                    logger.warning(f"Could not delete from Chroma: {e}")
            else:
                self.storage["embeddings"].pop(job_id, None)
                self.storage["metadata"].pop(job_id, None)
            
            # Remove from SQL database
            if self.db_manager:
                with self.db_manager.get_session() as session:
                    from app.data.models import JobEmbeddingDB
                    session.query(JobEmbeddingDB).filter(JobEmbeddingDB.job_id == job_id).delete()
                    session.commit()
            
            logger.debug(f"Deleted embedding for job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embedding for job {job_id}: {e}")
            return False
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings."""
        stats = {
            "embedding_model": self.embedding_model_name,
            "dimension": self.dimension,
            "storage_backend": self.storage_backend,
            "total_embeddings": 0
        }
        
        if self.storage_backend == "chroma":
            collection = self.storage["collection"]
            stats["total_embeddings"] = collection.count()
        else:
            stats["total_embeddings"] = len(self.storage["embeddings"])
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the vector store."""
        try:
            # Test embedding generation
            test_embedding = self.embedding_model.encode(["test query"])
            
            # Get stats
            stats = await self.get_embedding_stats()
            
            return {
                "status": "healthy",
                "embedding_model_loaded": True,
                "storage_backend": self.storage_backend,
                "stats": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Factory function for creating vector store instances
def create_vector_store(embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                       storage_backend: str = "chroma",
                       db_manager: Optional[DatabaseManager] = None) -> VectorStore:
    """Factory function to create a vector store instance."""
    return VectorStore(
        embedding_model=embedding_model,
        storage_backend=storage_backend,
        db_manager=db_manager
    )
