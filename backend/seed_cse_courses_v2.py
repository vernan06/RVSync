from app.database import SessionLocal
from app.models.classroom import Classroom, Branch, YearLevel
from app.models.course import Course, CourseMaterial
from app.models.user import User
from app.models.assignment import Assignment, Submission, Test, TestResult
import app.models.chat
import app.models.career
# import app.models.test # Removed as it is in assignment.py

def seed_courses():
    db = SessionLocal()
    try:
        # 1. Find 2nd Year CSE Classrooms
        # We look for classrooms that are Branch.CSE and YearLevel.SECOND
        # (Assuming sections A-E exist)
        
        classrooms = db.query(Classroom).filter(
            Classroom.branch == Branch.CSE,
            Classroom.year_level == YearLevel.SECOND
        ).all()
        
        if not classrooms:
            print("No 2nd Year CSE classrooms found. Please run seed_cse.py first.")
            return

        print(f"Found {len(classrooms)} classrooms. Seeding courses for each...")

        # Course Data
        sem3_courses = [
            {
                "name": "Linear Algebra and Probability Theory",
                "code": "21MAT31",
                "credits": 4,
                "description": "Vector spaces, linear transformations, eigenvalues, random variables, probability distributions, sampling theory, and inferential statistics with MATLAB implementation.",
                "instructor": "Dr. Mathematics"
            },
            {
                "name": "Data Structures and Applications",
                "code": "21CS32",
                "credits": 4,
                "description": "Stacks, queues, linked lists, trees, heaps, graphs, and hashing with practical lab implementations in C/C++/Python/Java.",
                "instructor": "Prof. CS"
            },
            {
                "name": "Applied Digital Logic Design and Computer Organisation",
                "code": "21CS33",
                "credits": 4,
                "description": "Arithmetic operations, Boolean simplification, binary adders, flip-flops, registers, counters, basic computer structure, instruction set architecture, and memory systems.",
                "instructor": "Prof. Electronics"
            },
            {
                "name": "Operating Systems",
                "code": "21CS34",
                "credits": 4,
                "description": "Process management, memory management, file systems, synchronization, deadlocks, and virtual memory with practical implementation using UNIX/Linux system calls and pthread library.",
                "instructor": "Prof. OS"
            },
            {
                "name": "Design Thinking Lab",
                "code": "21DTL35",
                "credits": 2,
                "description": "Practical course where students work in teams to solve societal problems through empathy, ideation, design, prototyping, and testing phases.",
                "instructor": "Prof. Design"
            },
            {
                "name": "Bridge Course C Programming (Audit)",
                "code": "21BCP36",
                "credits": 0,
                "description": "Mandatory audit course covering programming fundamentals, data types, control structures, arrays, strings, functions, structures, and pointers.",
                "instructor": "Prof. C"
            },
            # Basket Courses Group A
            {
                "name": "Environment & Sustainability (Group A)",
                "code": "21CIV37",
                "credits": 1,
                "description": "Understanding environmental systems, pollution, and sustainable development goals.",
                "instructor": "Prof. Env"
            },
            {
                "name": "Material Science for Engineers (Group A)",
                "code": "21ME37",
                "credits": 1,
                "description": "Structure and properties of materials, crystals, defects, and processing.",
                "instructor": "Prof. Mech"
            },
             {
                "name": "Bio Safety Standards and Ethics (Group A)",
                "code": "21BT37",
                "credits": 1,
                "description": "Biosafety levels, GMOs, ethical issues in biotechnology.",
                "instructor": "Prof. Bio"
            }
        ]

        sem4_courses_preview = [
            {
                "name": "[Preview] Discrete Mathematical Structures and Combinatorics",
                "code": "21MAT41",
                "credits": 4,
                "description": "Counting principles, recurrence relations, logic, relations, functions, group theory, coding theory, and graph theory.",
                "instructor": "TBD"
            },
            {
                "name": "[Preview] Design and Analysis of Algorithms",
                "code": "21CS42",
                "credits": 4,
                "description": "Brute force, divide and conquer, dynamic programming, greedy techniques, backtracking, branch and bound, and NP-completeness.",
                "instructor": "TBD"
            },
            {
                "name": "[Preview] IoT and Embedded Computing",
                "code": "21CS43",
                "credits": 4,
                "description": "ARM microcontrollers, embedded systems design, digital/analog interfacing, timers, interrupts, IoT concepts, and cloud platforms.",
                "instructor": "TBD"
            },
            {
                "name": "[Preview] Computer Networks",
                "code": "21CS44",
                "credits": 4,
                "description": "Network models, TCP/IP, data link layer, routing, congestion control, internetworking, and transport layer protocols.",
                "instructor": "TBD"
            },
            {
                "name": "[Preview] Universal Human Values",
                "code": "21UHV45",
                "credits": 1,
                "description": "Self-harmony, family relationships, societal harmony, and nature coexistence.",
                "instructor": "TBD"
            },
             {
                "name": "[Preview] Bridge Course Mathematics (Audit)",
                "code": "21MAT46",
                "credits": 0,
                "description": "Partial differentiation, vector differentiation, differential equations, and numerical methods.",
                "instructor": "TBD"
            }
            # Omitted electives/Ability enhancement as generic placeholders for now 
            # or add if needed:
            # Elective Group B
            # Ability Enhancement Group C
        ]

        all_courses = sem3_courses + sem4_courses_preview

        for classroom in classrooms:
            print(f"  Classroom: {classroom.code}")
            for course_data in all_courses:
                # Check if course exists in this classroom
                existing = db.query(Course).filter(
                    Course.classroom_id == classroom.id,
                    Course.code == course_data["code"]
                ).first()
                
                if existing:
                    # Update fields just in case
                    existing.name = course_data["name"]
                    existing.description = course_data["description"]
                    existing.credits = course_data["credits"]
                    existing.instructor = course_data["instructor"]
                    print(f"    Updated {course_data['code']}")
                else:
                    new_course = Course(
                        classroom_id=classroom.id,
                        name=course_data["name"],
                        code=course_data["code"],
                        description=course_data["description"],
                        credits=course_data["credits"],
                        instructor=course_data["instructor"]
                    )
                    db.add(new_course)
                    print(f"    Added {course_data['code']}")
        
        db.commit()
        print("Done seeding courses!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_courses()
