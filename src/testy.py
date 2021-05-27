class Test1:
    def main(self):
        print("First Main Function!")


class Test2(Test1):
    def main(self):
        print("Second main function!")
        super().main()


Test2().main()
