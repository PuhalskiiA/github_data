import logging

from datetime import datetime


class Token:
    def __init__(self, token: str) -> None:
        self.__value = token
        self.__expired_at: datetime | None = None

    @property
    def value(self) -> str:
        return self.__value

    @property
    def expired_at(self) -> datetime | None:
        return self.__expired_at

    @expired_at.setter
    def expired_at(self, expired_at: datetime) -> None:
        self.__expired_at = expired_at


class NoTokenAvailable(Exception):
    pass


class TokenProvider:
    def __init__(self, path: str) -> None:
        self.__tokens = self.__get_tokens(path)

    @staticmethod
    def __get_tokens(path: str) -> list[Token]:
        tokens = []

        try:
            with open(path, "r") as file:
                for line in file.readlines():
                    token_str = line.strip()
                    if token_str:
                        tokens.append(Token(token=token_str))

        except FileNotFoundError:
            logging.info(f"Ошибка при чтении токенов из файла: {path} не найден.")
        except Exception as e:
            logging.info(f"Ошибка при чтении файла: {e}")

        return tokens

    def get_token(self) -> Token:
        for token in self.__tokens:
            if token.expired_at is None:
                return token

            if (datetime.now() - token.expired_at).total_seconds() < 3600:
                continue
            else:
                token.expired_at = datetime.now()
                return token

        raise NoTokenAvailable()
