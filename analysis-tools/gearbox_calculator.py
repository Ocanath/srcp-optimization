
def calculate_srcp_ratio(N_r1, N_r2, N_p1):
    return -2*N_p1*N_r2/(2*N_p1*N_r1 - 2*N_p1*N_r2 - N_r1**2 + N_r1*N_r2)

    