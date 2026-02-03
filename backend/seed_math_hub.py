import sqlite3
import json
from datetime import datetime, timedelta

def seed_math_content():
    db_path = "rvsync.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get CSE-2E ID (it was 10 in the last run)
    cursor.execute("SELECT id FROM classrooms WHERE code = 'CSE-2E'")
    classroom_id = cursor.fetchone()[0]
    
    # 1. Update MAT231TC with Detailed Syllabus
    mat_syllabus = [
        {
            "unit": "Unit I",
            "title": "Linear Algebra – I",
            "topics": ["Vector spaces, subspaces, linear dependence/independence, basis, dimension", 
                       "Four fundamental subspaces, rank–nullity theorem", 
                       "Linear transformations: matrix representation, kernel & image", 
                       "Dilation, reflection, projection, rotation matrices", 
                       "Implementation using MATLAB"]
        },
        {
            "unit": "Unit II",
            "title": "Linear Algebra – II",
            "topics": ["Inner products, orthogonal matrices", 
                       "Orthogonal/orthonormal bases, Gram–Schmidt, QR-factorization", 
                       "Eigenvalues/eigenvectors (recap), diagonalization (symmetric matrices), SVD", 
                       "Implementation using MATLAB"]
        },
        {
            "unit": "Unit III",
            "title": "Random Variables",
            "topics": ["Discrete/continuous random variables, PMF, PDF, CDF, mean, variance", 
                       "Joint PMF/PDF, conditional distribution, independence", 
                       "Covariance, correlation", 
                       "Implementation using MATLAB"]
        },
        {
            "unit": "Unit IV",
            "title": "Probability Distributions and Sampling Theory",
            "topics": ["Binomial, Poisson, Exponential, Normal distributions", 
                       "Sampling, sampling distributions (with/without replacement)", 
                       "Standard error; sampling distributions of means (known), proportions; differences & sums", 
                       "Implementation using MATLAB"]
        },
        {
            "unit": "Unit V",
            "title": "Inferential Statistics",
            "topics": ["Statistical inference basics; hypothesis testing (null/alternative)", 
                       "Type I/II errors, significance level, one-/two-tailed tests, p-value", 
                       "Large/small sample tests: F, Chi-square, Z, t-test", 
                       "Implementation using MATLAB"]
        }
    ]
    
    cursor.execute("UPDATE courses SET description = ? WHERE code = 'MAT231TC'", (json.dumps(mat_syllabus),))
    
    # 2. Add CS241AT (Discrete Math)
    cs_syllabus = [
        {
            "unit": "Unit I",
            "title": "Counting + Recurrences",
            "topics": ["Rule of sum/product, permutations, combinations, inclusion–exclusion", "Recurrence relations, Generating functions"]
        },
        {
            "unit": "Unit II",
            "title": "Logic",
            "topics": ["Connectives, truth tables, tautologies", "Logical equivalence, rules of inference", "Quantifiers, proofs"]
        },
        {
            "unit": "Unit III",
            "title": "Relations and Functions",
            "topics": ["Partial orders, Hasse diagrams", "Stirling numbers", "Growth of functions"]
        },
        {
            "unit": "Unit IV",
            "title": "Group Theory + Coding Theory",
            "topics": ["Groups, abelian groups", "Lagrange’s theorem", "Hamming metric, parity-check matrices"]
        },
        {
            "unit": "Unit V",
            "title": "Graph Theory + Trees",
            "topics": ["Eulerian & Hamiltonian graphs", "Graph coloring", "Trees, rooted trees, spanning trees"]
        }
    ]
    
    # Check if CS241AT exists
    cursor.execute("SELECT id FROM courses WHERE code = 'CS241AT'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO courses (classroom_id, name, code, instructor, credits, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (classroom_id, "Discrete Mathematical Structures and Combinatorics", "CS241AT", "TBA", 4, json.dumps(cs_syllabus)))
        print("Added CS241AT.")
    else:
        cursor.execute("UPDATE courses SET description = ? WHERE code = 'CS241AT'", (json.dumps(cs_syllabus),))

    # 3. Add Sample Tests for MAT231TC (ID needed)
    cursor.execute("SELECT id FROM courses WHERE code = 'MAT231TC'")
    mat_id = cursor.fetchone()[0]
    
    # Clear old tests to avoid duplicates
    cursor.execute("DELETE FROM tests WHERE course_id = ?", (mat_id,))
    
    test_questions = [
        {
            "question": "What is the dimension of the subspace spanned by (1,0,0) and (0,1,0)?",
            "options": ["1", "2", "3", "0"],
            "answer": "2"
        },
        {
            "question": "The kernel of a linear transformation T: V -> W is a subspace of:",
            "options": ["V", "W", "Both", "Neither"],
            "answer": "V"
        },
        {
            "question": "A matrix is diagonalizable if it has:",
            "options": ["Distict eigenvalues", "n linearly independent eigenvectors", "Positive determinant", "No zero rows"],
            "answer": "n linearly independent eigenvectors"
        }
    ]
    
    cursor.execute("""
        INSERT INTO tests (course_id, title, description, total_points, time_limit, questions, is_published, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (mat_id, "Linear Algebra Quiz 1", "Basics of Vector Spaces and Transformations", 30.0, 15, json.dumps(test_questions), 1, 1))

    conn.commit()
    conn.close()
    print("Math content seeded successfully!")

if __name__ == "__main__":
    seed_math_content()
