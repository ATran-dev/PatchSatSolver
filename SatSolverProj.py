from pysat.solvers import Solver

"""
Does basic parsing of a cnf file to be used in sat calculation
"""
def parseCnfFile(filename):
    numVars = 0
    clauses = []
    clauseCount = 0
    
    with open(filename) as file:
        for line in file:
            if line.startswith("c"):
                continue
            elif (line.startswith("p")):
                parts = line.split()
                numVars = int(parts[2])
                clauseCount = int(parts[3])
            else:
                clause = []
                for num in line.split():
                    if (num != "0"):
                        clause.append(int(num))
                clauses.append(clause)
                
    return clauses, clauseCount, numVars

    
"""
Does basic Sat calculation on a cnf file
"""
def basicSatCalc():
    clauseList, numClause, numVar = parseCnfFile("cnfInputTest.txt")
    
    solver = Solver(name="glucose3")
    for clause in clauseList:
        solver.add_clause(clause)
    result = solver.solve()
    
    if result:
        print ("SAT")
        print (solver.get_model())
    else:
        print ("UNSAT")

    solver.delete()
    
    return result

def eqCheck(implClauses, specClauses):
    # check (!impl AND spec), then check (impl AND !spec)
    implAndNotSpecSat = False
    notImplAndSpecSat = False
    
    #(impl AND !spec)
    solver = Solver(name="glucose3")
    for clause in implClauses:
        solver.add_clause(clause)
    for clause in specClauses:
        solver.add_clause([-lit for lit in clause])
        
    implAndNotSpecSat = solver.solve()
    solver.delete()
    
    #(!impl AND Spec)
    solver = Solver(name="glucose3")
    for clause in specClauses:
        solver.add_clause(clause)
    for clause in implClauses:
        solver.add_clause([-lit for lit in clause])
        
    notImplAndSpecSat = solver.solve()
    solver.delete()

    # if either SAT, CIRCUITS NOT EQ
    # if BOTH UNSAT, CIRCUITS EQ
    if (implAndNotSpecSat == True or notImplAndSpecSat == True):
        print("circuits are not equivalent")
    if (implAndNotSpecSat == False and notImplAndSpecSat == False):
        print("circuits are equivalent")
    
    return

def iterativeSatCalc(implClauseList, specClauseList, paramVars, inVars):
    # 1) Let circuit(X, In) be the formula representing the circuit 
    #    with given transformations encoded.
    #    - X: set of parameter variables for transformations
    #    - In: set of primary input variables of the circuit


    # 2) Let spec(In) be the formula representing the specification.
    
    inVars = set(inVars)        
    paramVars = set(paramVars)  

    # 3) Initialize:
    #    k = 0  # number of test vectors found
    #    TestSet = []  # initially empty
    
    k = 0
    testSet = []

    # 4) Define the target formula to check:
    #    Target = (circuit(X, In) != spec(In))
    #    - X and In are variables to be solved by a SAT solver
    
    miter_solver = Solver(name="glucose3")
    for clause in implClauseList:
        miter_solver.add_clause(clause)
    for clause in specClauseList:
        miter_solver.add_clause(clause)
        
    # 5) Check if Target is satisfiable using a SAT solver.
    #    - This is a normal SAT problem.
    
    # 6) If Target is SAT:
    #    - Increment k: k = k + 1
    #    - Let (xk, ink) be a solution found by the SAT solver
    #    - Add the primary input ink to TestSet
    #      TestSet = TestSet ∪ {ink}
    #    - Refine Target by blocking this solution:
    #      Target = Target ∧ (circuit(X, ink) == spec(ink))
    #    - Go back to step 5 to search for another counterexample
    
    while True:
        if not miter_solver.solve():
            # UNSAT: no counterexample found, proceed to final check
            break

        model = miter_solver.get_model()
        k += 1

        # Extract input assignments only
        inK = [lit for lit in model if abs(lit) in inVars]
        testSet.append(inK)

        # Block this input assignment so we find a new one next iteration
        blocking_clause = [-lit for lit in inK]
        miter_solver.add_clause(blocking_clause)

    miter_solver.delete()

    # 7) If Target is UNSAT:
    #    - Check if the formula below is satisfiable:
    #      (circuit(X, in1) == spec(in1)) ∧ 
    #      (circuit(X, in2) == spec(in2)) ∧ ... ∧ 
    #      (circuit(X, ink) == spec(ink)) for all ink in TestSet
    #    - If SAT:
    #      - Any solution (x, in) corresponds to a correct set of transformations X
    #      - This implicitly represents the set of all correct circuits
    #    - Else:
    #      - No correct set of transformations exists
    
    if not testSet:
        print("Circuits equivalent for all inputs found")
        return

    # Final check: does any X (param assignment) satisfy all test vectors?
    final_solver = Solver(name="glucose3")

    for clause in implClauseList:
        final_solver.add_clause(clause)

    for inK in testSet:
        # Force this specific input assignment as assumptions
        assumptions = [lit for lit in inK]
        if not final_solver.solve(assumptions=assumptions):
            print("No solution exists")
            final_solver.delete()
            return

    print("Solution exists:", final_solver.get_model())
    final_solver.delete()

    
def main():
    
    print("1: EQ Check, 2: Basic SAT Call, 3: IterativePatchSAT")
    op = int(input("Enter an operation: "))
    
    """ 
    Eq Check
    """
    if (op == 1):
        specClauseList, specNumClauses, specVars = parseCnfFile("spec.txt")
        implClauseList, implNumClauses, implVars = parseCnfFile("impl.txt")
        eqCheck(implClauseList, specClauseList)    
    """
    Simple Sat Calc
    """
    if (op == 2):
        basicSatCalc()
    
    """
    Iterative Calc
    """
    if (op == 3):
        specClauseList, specNumClauses, specVars = parseCnfFile("spec.txt")
        implClauseList, implNumClauses, implVars = parseCnfFile("impl.txt")
        inVars = list(range(1, implVars + 1))     
        paramVars = list(range(implVars + 1, specVars + 1))
        iterativeSatCalc(implClauseList, specClauseList, paramVars, inVars)
        
        

if __name__ == "__main__":
    main()