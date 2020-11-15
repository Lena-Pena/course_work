def decorator(fn):
    def decorated(*args, **kwargs):
        result = fn(*args, **kwargs)

        return result * 2

    return decorated


@decorator
def fun_to_decorate(a, b, c):
    return a + b + c


fun_to_decorate = decorator(fn=fun_to_decorate)


def multiply_by_n(n):
    def inner_decorator(fn):
        def decorated(*args, **kwargs):
            result = fn(*args, **kwargs)

            return result * n

        return decorated

    return inner_decorator


@multiply_by_n(4)
def fun_to_decorate_2(a, b, c):
    return a + b + c


fun_to_decorate_2 = multiply_by_n(4)(fn=fun_to_decorate_2)

multiply_by_four = multiply_by_n(4)
fun_to_decorate_2 = multiply_by_four(fn=fun_to_decorate_2)




if __name__ == '__main__':
    print(fun_to_decorate(1, b=2, c=3))
