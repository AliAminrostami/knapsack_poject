# Read data from file
def reading(category, problem_num):
    "Function to read data from a file" 
    with open(f"Data\\mknapcb{category}.txt", 'r', encoding='utf-8') as file: 
        for i in range(30):

            m_n = list(map(int,file.readline().split()))
            nI = m_n[0] # nI = number of items
            nK = m_n[1] # nK = number of knapstacks

            benefit = []
            while len(benefit) < m_n[0]:
                benefit.extend(map(float, file.readline().split()))

            weight = [[] for _ in range(m_n[1])]
            for j in range(m_n[1]):
                while len(weight[j]) < m_n[0]:
                    weight[j].extend(map(float, file.readline().split()))

            capacity = []
            while len(capacity) < m_n[1]:
                capacity.extend(map(float, file.readline().split()))

            if i == problem_num:
                break
    return nI, nK , benefit, weight, capacity 