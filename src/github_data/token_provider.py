import logging

from datetime import datetime


class Token:
    def __init__(self, token: str):
        self.__value = token
        self.__expired_at = None

    def get_value(self) -> str:
        return self.__value

    def set_expired_at(self, expired_at: datetime) -> None:
        self.__expired_at = expired_at

    def get_expired_at(self) -> datetime:
        return self.__expired_at

# Не забыть выставить expired_at

class TokenProvider:
    def __init__(self, path: str) -> None:
        self.__tokens = self.__get_tokens(path)

    @staticmethod
    def __get_tokens(path: str) -> list[Token]:
        tokens = []

        try:
            with open(path, 'r') as file:
                lines = file.read().splitlines()

                for line in lines:
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
            if token.get_expired_at() is None:
                return token

            if (datetime.now() - token.get_expired_at()).total_seconds() < 3600:
                continue
            else:
                token.set_expired_at(None)
                return token
