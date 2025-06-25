# hello world 2

Time to test directives.

- because I can
- yes !

.. test1:: arg1 arg2
    :option1: valueA

    content line 1

    content line 3

.. test1:: arg3 arg4

    content line 1

    content line 3


.. test1:: arg5 arg6
    content line 1

    content line 3

.. test1:: arg7 arg8

        content line 1

    content line 3

intermediate text before test2

.. test2:: 
    :option1: value1
    :option2: value2

.. test2:: 

    :option1: valueE
    :option2: valueF

.. test2:: 
    :option1: this is some very long text  
        that wraps multiple line

        to test the multiline feature.
    :option2: valueG

.. test3:: argA argB

.. test3:: argC argD
text without line break

start of another paragraph