class A:
    def __init_subclass__(cls, **kwargs):
        print(f"A.__init_subclass__ called for {cls.__name__}")
        print(f"kwargs: {kwargs}")
        super().__init_subclass__(**kwargs)


class B:
    def __init_subclass__(cls, color=None, **kwargs):
        print(f"B.__init_subclass__ called for {cls.__name__}, color={color}")
        print(f"kwargs: {kwargs}")
        super().__init_subclass__(**kwargs)


class C(A, B):
    pass


print("\n--- Define D after C ---\n")


# When you define this class, it will trigger __init_subclass__:
class D(C, color="red"):
    pass


print("\n--- Now try defining another one ---\n")


class E(C, color="blue"):
    pass


print("\n--- What if we don't pass color? ---\n")


class F(C):
    pass


print("\n--- Try commenting out super() calls to see what breaks! ---")
