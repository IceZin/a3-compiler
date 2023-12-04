int variavel1 = 2 + 4 * 9 / 2
string variavel2 = "Programa de teste 1 while loop"
string variavel3 = "Programa de teste 1 for loop"
int intvar = variavel1 + 4

if variavel1 > 20 run
    show(variavel2)
    show(variavel1)

    while variavel1 > 10 run
        variavel1 = variavel1 - 1
        show("Valor de variavel1 eh")
        show(variavel1)
    end
else run
    show(variavel3)

    for (int i = 0; i < 10; i = i + 1) run
        variavel1 = variavel1 + i
        show("Valor de variavel1 eh")
        show(variavel1)
    end
end