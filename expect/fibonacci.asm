JMP main
t_var_m_1:
    0
t_var_n_2:
    0
t_var_k_3:
    0
t_var_count_4:
    0
main:
	PUSH 1
	SAVE t_var_m_1
	PUSH 1
	SAVE t_var_n_2
	PUSH 1
	SAVE t_var_k_3
	PUSH 0
	SAVE t_var_count_4
t_while_start_5:
	LOAD t_var_count_4
	PUSH 20
	CMPLTE
	JE t_while_end_6
	LOAD t_var_k_3
	PRINT
	POP
	LOAD t_var_n_2
	SAVE t_var_k_3
	LOAD t_var_m_1
	LOAD t_var_n_2
	ADD
	SAVE t_var_n_2
	LOAD t_var_k_3
	SAVE t_var_m_1
	LOAD t_var_count_4
	PUSH 1
	ADD
	SAVE t_var_count_4
	JMP t_while_start_5
t_while_end_6:
	HALT
