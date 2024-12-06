from typing import Dict, List

from kiss_ai_stack.core.ai_clients.ai_client_abc import AIClientAbc
from kiss_ai_stack.core.dbs.db_abc import VectorDBAbc
from kiss_ai_stack.core.models.core.rag_response import ToolResponse
from kiss_ai_stack.core.models.enums.tool_kind import ToolKind
from kiss_ai_stack.core.utilities.logger import LOG


class Tool:
    """
    A unified interface for processing AI tasks with optional vector database support.
    This class handles query processing and document storage while ensuring sensitive data is protected.

    Attributes:
        __tool_kind (ToolKind): The type of the tool (e.g., RAG, PROMPT).
        __ai_client (AIClientAbc): The AI client used for query processing.
        __vector_db (VectorDBAbc | None): The optional vector database for document storage and retrieval.
    """

    def __init__(
            self,
            tool_kind: ToolKind,
            ai_client: AIClientAbc,
            vector_db: VectorDBAbc = None
    ):
        """
        Initialize a Tool instance.

        Args:
            tool_kind (ToolKind): The type of tool (e.g., RAG, PROMPT).
            ai_client (AIClientAbc): The AI client instance.
            vector_db (VectorDBAbc, optional): The vector database instance. Defaults to None.
        """
        self.__tool_kind = tool_kind
        self.__ai_client = ai_client
        self.__vector_db = vector_db
        LOG.info(f'Tool :: Tool initialized with kind: {self.__tool_kind}')

    def store_docs(self, documents: List[str], metadata_list: List[Dict]) -> List[str]:
        """
        Store documents in the vector database.

        Args:
            documents (List[str]): A list of documents to be stored.
            metadata_list (List[Dict]): A list of metadata dictionaries for the documents.

        Returns:
            List[str]: A list of document IDs generated by the vector database.

        Raises:
            IOError: If the vector database is not initialized.
        """
        if self.__vector_db:
            LOG.info(f'Tool :: Storing {len(documents)} documents in the vector database.')
            try:
                ids = self.__vector_db.push(documents=documents, metadata_list=metadata_list)
                LOG.info('Tool :: Documents successfully stored. IDs generated.')
                return ids
            except Exception as e:
                LOG.error(f'Tool :: Failed to store documents: {str(e)}')
                raise
        else:
            error_message = 'Tool :: Vector DB has not been initialized.'
            LOG.error(error_message)

    def process_query(self, query: str) -> ToolResponse | None:
        """
        Process a query using the AI client and optional vector database.

        Args:
            query (str): The query string to be processed.

        Returns:
            ToolResponse | None: The response generated by the tool.

        Raises:
            Exception: If query processing fails for any reason.
        """
        LOG.info(f'Processing query with tool kind: {self.__tool_kind}')
        try:
            tool_response = None

            if self.__tool_kind == ToolKind.RAG:
                LOG.info('Tool :: Performing retrieval-augmented generation (RAG) for query processing.')
                chunk_result = self.__vector_db.retrieve(query)
                chunks = chunk_result['documents'][0]
                LOG.debug('Tool :: Retrieved chunk metadata, not logging content.')
                answer = self.__ai_client.generate_answer(query, chunks)
                LOG.info('Tool :: Answer generated by AI client, not logging content.')

                tool_response = ToolResponse(
                    answer=answer,
                    docs=chunks,
                    metadata=chunk_result['metadatas'],
                    distances=chunk_result['distances']
                )
            else:
                LOG.info('Tool :: Using direct prompt mode for query processing.')
                answer = self.__ai_client.generate_answer(query=query)
                LOG.info('Tool :: Answer generated by AI client, ****')
                tool_response = ToolResponse(answer=answer)

            return tool_response
        except Exception as e:
            LOG.error('Tool :: Failed to process query')
            raise e
