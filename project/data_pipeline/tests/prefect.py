from prefect import flow, task


@task(name="say-hello")
def say_hello(name: str = "World"):
    message = f"Hello, {name}!"
    print(message)
    return message


@flow(name="hello-world-with-task",log_prints=True)
def hello_world_with_task(name: str = "World"):
    print("Flow started - about to run a task")

    results = say_hello(name)

    print("Flow completed")
    return results


if __name__ == "__main__":
    result = hello_world_with_task()
    print(f"Result: {result}")