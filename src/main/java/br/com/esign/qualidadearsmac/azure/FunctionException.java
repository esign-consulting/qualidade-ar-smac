package br.com.esign.qualidadearsmac.azure;

public class FunctionException extends RuntimeException {
    
    private static final long serialVersionUID = 1L;

    public FunctionException(String message) {
        super(message);
    }

    public FunctionException(String message, Throwable cause) {
        super(message, cause);
    }

    public FunctionException(Throwable cause) {
        super(cause);
    }

}
