from writing_an_interpreter.objects import String


def test_can_hash_string_keys():
    hello_1 = String("hello")
    hello_2 = String("hello")
    diff_1 = String("different")
    diff_2 = String("different")

    assert hello_1.hash() == hello_2.hash()
    assert diff_1.hash() == diff_2.hash()
    assert hello_1.hash() != diff_1.hash()
